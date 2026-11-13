"""Multi-session GRPO / RLOO with FULL fine-tuning (no LoRA).

Same objective as grpo.py (episode-level reward = frozen reader EM, advantage applied to
every writer generation in the trajectory, one on-policy update per batch), but all
weights of the writer are trained.

Layout (2 GPUs):
  GPU 0: trainer. fp32 master weights, bf16 autocast, 8-bit AdamW, gradient checkpointing,
         optional frozen bf16 reference model for a k3 KL penalty (--beta > 0).
  GPU 1: writer sampler (vLLM server with NCCL weight transfer) + reader (vLLM server).
After every optimizer step the trainer streams bf16 copies of all weights to the sampler.

  VLLM_SERVER_DEV_MODE=1 CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-1.7B --port 8402 \
      --weight-transfer-config '{"backend": "nccl"}' --gpu-memory-utilization 0.30 --max-model-len 4096
  CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --gpu-memory-utilization 0.50 --max-model-len 2048
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_full --episodes train_2s.jsonl --aliases value_aliases.json \
      --steps 20 --algo grpo --out runs/grpo_full_timing
"""
from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import torch

from .baselines import BUDGET_TOKENS, truncate
from .grpo import advantages, reader_rewards
from .writer import build_prompt, build_teacher_prompt, clean


def token_logprobs(model, ids, att, start):
    """Log-probs of ids[:, start+1:] given the prefix; only completion positions get logits."""
    L = ids.shape[1]
    with torch.autocast("cuda", dtype=torch.bfloat16):
        logits = model(input_ids=ids, attention_mask=att, logits_to_keep=L - start).logits[:, :-1]
    tgt = ids[:, start + 1:]
    logits = logits.float()
    return logits.gather(-1, tgt[..., None]).squeeze(-1) - torch.logsumexp(logits, -1)


def pg_backward(policy, ref, tok, gens, active, adv, args):
    """GRPO/RLOO policy-gradient loss (+ optional k3 KL), accumulated over micro-batches."""
    total_loss, total_kl, n_tok = 0.0, 0.0, 0
    for k in range(0, len(active), args.micro_batch):
        mb = active[k:k + args.micro_batch]
        seqs = [pid + cid for _, pid, cid, _ in mb]
        L = max(map(len, seqs))
        ids = torch.full((len(mb), L), tok.pad_token_id, dtype=torch.long)
        att = torch.zeros((len(mb), L), dtype=torch.long)
        cm = torch.zeros((len(mb), L), dtype=torch.float)
        for j, (_, pid, cid, _) in enumerate(mb):
            n = len(pid) + len(cid)
            ids[j, :n] = torch.tensor(pid + cid)
            att[j, :n] = 1
            cm[j, len(pid):n] = 1.0
        ids, att, cm = ids.cuda(), att.cuda(), cm.cuda()
        start = min(len(pid) for _, pid, _, _ in mb) - 1
        lp = token_logprobs(policy, ids, att, start)
        m = cm[:, start + 1:]
        a = torch.tensor([adv[i] for i, _, _, _ in mb], device=lp.device)
        per_seq = (lp * m).sum(-1) / args.max_new  # Dr.GRPO-style constant normalizer
        loss = -(a * per_seq).sum() / max(1, len(gens))
        if ref is not None:
            with torch.no_grad():
                rlp = token_logprobs(ref, ids, att, start)
            d = rlp - lp
            kl = ((torch.exp(d) - d - 1) * m).sum() / m.sum().clamp(min=1)
            loss = loss + args.beta * kl * len(mb) / max(1, len(active))
            total_kl += kl.item() * len(mb)
        loss.backward()
        total_loss += loss.item()
        n_tok += int(m.sum().item())
        del lp
    return total_loss, total_kl, n_tok


def opsd_backward(policy, tok, gens, max_new):
    """On-policy self-distillation: for each student rollout, per-token full-vocabulary reverse
    KL(student || teacher), where the teacher is the same (current) model, gradient-free, prompted
    with derivable hints. Normalized like the PG loss (constant max_new per sequence)."""
    total, n_tok = 0.0, 0
    for _, pid, cid, tprompt in gens:
        if not cid:
            continue
        tid = tok(tprompt, add_special_tokens=False)["input_ids"]
        c = torch.tensor(cid, device="cuda")[None]
        s_ids = torch.cat([torch.tensor(pid, device="cuda")[None], c], 1)
        t_ids = torch.cat([torch.tensor(tid, device="cuda")[None], c], 1)
        keep = len(cid) + 1
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
            t_logits = policy(input_ids=t_ids, logits_to_keep=keep).logits[:, :-1].float()
        with torch.autocast("cuda", dtype=torch.bfloat16):
            s_logits = policy(input_ids=s_ids, logits_to_keep=keep).logits[:, :-1].float()
        s_lp = torch.log_softmax(s_logits, -1)
        t_lp = torch.log_softmax(t_logits, -1)
        kl_tok = (s_lp.exp() * (s_lp - t_lp)).sum(-1)  # [1, len(cid)]
        loss = kl_tok.sum() / max_new / len(gens)
        loss.backward()
        total += loss.item()
        n_tok += len(cid)
        del t_logits, s_logits, s_lp, t_lp
    return total, n_tok



def frozen_teacher_logprobs(url, model, tok, gens):
    """Log-prob of each sampled completion token under the FROZEN teacher (initial weights) given the
    hint-augmented teacher prompt. vLLM prompt_logprobs=0 always returns the actual token's log-prob."""
    import requests
    seqs, starts = [], []
    for _, _, cid, tprompt in gens:
        tid = tok(tprompt, add_special_tokens=False)["input_ids"]
        seqs.append(tid + list(cid))
        starts.append(len(tid))
    out = [None] * len(seqs)

    def call(lo, hi):
        r = requests.post(f"{url}/v1/completions", timeout=900, json={
            "model": model, "prompt": seqs[lo:hi], "max_tokens": 1, "temperature": 1.0, "prompt_logprobs": 0})
        r.raise_for_status()
        for k, ch in enumerate(sorted(r.json()["choices"], key=lambda c: c["index"])):
            j = lo + k
            plp = ch["prompt_logprobs"]
            vals = []
            for pos in range(starts[j], len(seqs[j])):
                entry = plp[pos]
                tok_id = str(seqs[j][pos])
                vals.append(entry[tok_id]["logprob"] if entry and tok_id in entry else float("-inf"))
            out[j] = vals

    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda lo: call(lo, min(lo + 16, len(seqs))), range(0, len(seqs), 16)))
    return out


def opsd_frozen_backward(policy, gens, t_lps, max_new, clip=10.0):
    """On-policy distillation from a frozen teacher with the per-token reverse-KL estimator on sampled
    tokens: advantage_t = log p_T(x_t) - log p_S(x_t) (detached, clipped), loss = -sum_t A_t log p_S(x_t)."""
    total, n_tok = 0.0, 0
    for (_, pid, cid, _), t_lp in zip(gens, t_lps):
        if not cid:
            continue
        ids = torch.tensor(list(pid) + list(cid), device="cuda")[None]
        keep = len(cid) + 1
        with torch.autocast("cuda", dtype=torch.bfloat16):
            logits = policy(input_ids=ids, logits_to_keep=keep).logits[:, :-1].float()
        tgt = torch.tensor(cid, device="cuda")[None]
        s_lp = (logits.gather(-1, tgt[..., None]).squeeze(-1) - torch.logsumexp(logits, -1))[0]
        t = torch.tensor(t_lp, device="cuda", dtype=torch.float)
        t = torch.where(torch.isfinite(t), t, torch.full_like(t, -30.0))
        a = (t - s_lp.detach()).clamp(-clip, clip)
        loss = -(a * s_lp).sum() / max_new / len(gens)
        loss.backward()
        total += loss.item()
        n_tok += len(cid)
        del logits
    return total, n_tok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--aliases", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--writer-url", default="http://127.0.0.1:8402")
    ap.add_argument("--reader-url", default="http://127.0.0.1:8401")
    ap.add_argument("--reader-model", default="Qwen/Qwen3-4B")
    ap.add_argument("--teacher-url", default="http://127.0.0.1:8403",
                    help="opsd_frozen: vLLM server with the FROZEN initial writer (no weight sync)")
    ap.add_argument("--algo", choices=["grpo", "rloo", "opsd", "opsd_frozen"], default="grpo",
                    help="opsd: on-policy self-distillation, per-token reverse KL to the same model "
                         "prompted with derivable hints (hints.py); reward only logged")
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--episodes-per-step", type=int, default=4)
    ap.add_argument("--group", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-6)
    ap.add_argument("--beta", type=float, default=0.0, help="k3 KL weight to the frozen initial model")
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--micro-batch", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--save", action="store_true", help="save final weights (bf16) to OUT/final")
    ap.add_argument("--local-frac", type=float, default=0.0,
                    help="LoGo-style local groups (Memory-R2): for this fraction of episodes per step, roll out "
                         "--group candidates for the LAST session from one shared intermediate memory and "
                         "add their within-group advantages (GRPO/RLOO only)")
    args = ap.parse_args()

    import bitsandbytes as bnb
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl.generation.vllm_client import VLLMClient

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    aliases = json.loads(args.aliases.read_text())
    eps = [json.loads(l) for l in args.episodes.open()]
    tok = AutoTokenizer.from_pretrained(args.model)
    reader_tok = AutoTokenizer.from_pretrained(args.reader_model)

    policy = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32).cuda()
    policy.gradient_checkpointing_enable()
    policy.config.use_cache = False
    ref = None
    if args.beta > 0:
        ref = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16).cuda().eval()
        ref.requires_grad_(False)
    opt = bnb.optim.AdamW8bit(policy.parameters(), lr=args.lr, betas=(0.9, 0.99), weight_decay=0.0)

    client = VLLMClient(base_url=args.writer_url, connection_timeout=900)
    client.init_communicator(device=0)
    params = [(n, p) for n, p in policy.named_parameters()]
    meta = [(n, "bfloat16", list(p.shape)) for n, p in params]

    def sync():
        client.update_named_params(meta, ((n, p.data.to(torch.bfloat16)) for n, p in params))
        client.reset_prefix_cache()

    t_sync0 = time.time()
    sync()  # sampler starts from exactly the trainer's weights
    print(json.dumps({"initial_sync_s": round(time.time() - t_sync0, 2)}), flush=True)
    log = (args.out / "train_log.jsonl").open("a")

    for step in range(args.steps):
        t0 = time.time()
        batch = random.sample(eps, args.episodes_per_step)
        trajs = [ep for ep in batch for _ in range(args.group)]
        memories = [""] * len(trajs)
        mem_hist = [[""] for _ in trajs]  # memory before each session
        gens = []  # (traj index, prompt ids, completion ids, teacher prompt text or None)
        for s in range(max(len(ep["sessions"]) for ep in batch)):
            idx = [i for i, ep in enumerate(trajs) if s < len(ep["sessions"])]
            prompts = [build_prompt(tok, memories[i], trajs[i]["sessions"][s], s) for i in idx]
            out = client.generate(prompts, n=1, temperature=args.temperature, top_p=1.0,
                                  max_tokens=args.max_new, logprobs=None)
            for i, pid, cid in zip(idx, out["prompt_ids"], out["completion_ids"]):
                tprompt = (build_teacher_prompt(tok, memories[i], trajs[i], s)
                           if args.algo in ("opsd", "opsd_frozen") else None)
                gens.append((i, pid, cid, tprompt))
                memories[i] = truncate(clean(tok.decode(cid, skip_special_tokens=True)), BUDGET_TOKENS)
                mem_hist[i].append(memories[i])
        # LoGo-style local branch: shared intermediate state -> G candidates for the last session
        local = []  # (episode index in batch, prompt ids, completion ids, final memory)
        if args.local_frac > 0 and args.algo in ("grpo", "rloo"):
            for b_i, ep in enumerate(batch):
                if random.random() >= args.local_frac or len(ep["sessions"]) < 2:
                    continue
                last = len(ep["sessions"]) - 1
                src = b_i * args.group + random.randrange(args.group)
                shared = mem_hist[src][last]
                out = client.generate([build_prompt(tok, shared, ep["sessions"][last], last)], n=args.group,
                                      temperature=args.temperature, top_p=1.0, max_tokens=args.max_new, logprobs=None)
                pid = out["prompt_ids"][0]  # one prompt, n completions
                for cid in out["completion_ids"]:
                    local.append((b_i, pid, cid, truncate(clean(tok.decode(cid, skip_special_tokens=True)), BUDGET_TOKENS)))
        t_roll = time.time()

        rewards = reader_rewards(args.reader_url, args.reader_model, reader_tok, memories,
                                 [ep["questions"] for ep in trajs], [ep["hidden"]["answers"] for ep in trajs], aliases)
        adv = advantages(rewards, args.group, args.algo) if args.algo in ("grpo", "rloo") else None
        local_rewards = []
        if local:
            local_rewards = reader_rewards(args.reader_url, args.reader_model, reader_tok, [m for *_, m in local],
                                           [batch[b]["questions"] for b, *_ in local],
                                           [batch[b]["hidden"]["answers"] for b, *_ in local], aliases)
            ladv = advantages(local_rewards, args.group, args.algo)
            base = len(trajs)
            for k, (b, pid, cid, _) in enumerate(local):
                gens.append((base + k, pid, cid, None))
            adv = adv + ladv
        t_rew = time.time()

        policy.train()
        opt.zero_grad(set_to_none=True)
        if args.algo == "opsd":
            total_loss, n_tok = opsd_backward(policy, tok, gens, args.max_new)
            active = gens
        elif args.algo == "opsd_frozen":
            t_lps = frozen_teacher_logprobs(args.teacher_url, args.model, tok, gens)
            total_loss, n_tok = opsd_frozen_backward(policy, gens, t_lps, args.max_new)
            active = gens
        else:
            active = [g for g in gens if abs(adv[g[0]]) > 1e-8]
            total_loss, total_kl, n_tok = pg_backward(policy, ref, tok, gens, active, adv, args)
        gnorm = torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0).item()
        opt.step()
        t_bwd = time.time()
        sync()
        t_end = time.time()

        rec = {"step": step, "algo": args.algo, "full_ft": True, "beta": args.beta,
               "reward_mean": sum(rewards) / len(rewards), "reward_std": float(torch.tensor(rewards).std()),
               "loss": total_loss, "kl": (total_kl / max(1, len(active)) if ref is not None and args.algo in ("grpo", "rloo") else None),
               "grad_norm": gnorm, "nan": math.isnan(total_loss),
               "frac_zero_adv_groups": sum(1 for i in range(0, len(rewards), args.group)
                                           if len(set(rewards[i:i + args.group])) == 1) / args.episodes_per_step,
               "mean_completion_tokens": sum(len(g[2]) for g in gens) / len(gens),
               "local_groups": len(local) // max(1, args.group), "local_reward_mean": (sum(local_rewards) / len(local_rewards)) if local_rewards else None,
               "t_rollout": round(t_roll - t0, 2), "t_reward": round(t_rew - t_roll, 2),
               "t_backward": round(t_bwd - t_rew, 2), "t_sync": round(t_end - t_bwd, 2),
               "t_step": round(t_end - t0, 2), "max_mem_gb": round(torch.cuda.max_memory_allocated() / 2**30, 2)}
        log.write(json.dumps(rec) + "\n")
        log.flush()
        print(json.dumps(rec), flush=True)
    if args.save:
        policy.to(torch.bfloat16).save_pretrained(args.out / "final")
        tok.save_pretrained(args.out / "final")


if __name__ == "__main__":
    main()
