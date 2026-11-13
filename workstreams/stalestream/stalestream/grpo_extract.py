"""GRPO on the line-level EXTRACTOR of the extract_rules pipeline (full fine-tuning, no LoRA).

The policy is the extractor (one JSON per stream line, extract.PROMPT, header context); the fixed
rules (aliases, audited sources dropped, latest date wins) and the frozen reader stay unchanged. The
reward is the same episode-level reader EM the GRPO writer is trained on, so the two arms differ only
in where the trainable model sits: end-to-end writer vs extractor inside a fixed pipeline.

Credit assignment uses line-level groups: per step, every line of each sampled episode is first
extracted greedily by the current policy; then for K random lines per episode, G alternative
extractions of that ONE line are sampled while all other lines stay at the greedy output. Each
alternative is resolved by the rules into a memory and scored by the reader; advantages are computed
within the G alternatives of a line. Line choice is uniform over non-header lines (no hidden labels).

Same layout as grpo_full.py: trainer on GPU 0; sampler (vLLM, NCCL weight transfer) and reader on GPU 1.
  python -m stalestream.grpo_extract --episodes train_2s.jsonl --aliases value_aliases.json \
      --mquake MQuAKE.json --steps 20 --out runs/grpo_extract_timing
"""
from __future__ import annotations

import argparse
import json
import math
import random
import time
from pathlib import Path

import torch

from .extract import grammar, is_header, line_prompt, parse_json, resolve_extracted
from .grpo import advantages, reader_rewards
from .grpo_full import pg_backward


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--aliases", type=Path, required=True)
    ap.add_argument("--mquake", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--writer-url", default="http://127.0.0.1:8402")
    ap.add_argument("--reader-url", default="http://127.0.0.1:8401")
    ap.add_argument("--reader-model", default="Qwen/Qwen3-4B")
    ap.add_argument("--context", choices=["header", "session"], default="header")
    ap.add_argument("--algo", choices=["grpo", "rloo"], default="grpo")
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--episodes-per-step", type=int, default=4)
    ap.add_argument("--lines-per-episode", type=int, default=8)
    ap.add_argument("--group", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-6)
    ap.add_argument("--max-new", type=int, default=192)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--micro-batch", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--save", action="store_true")
    args = ap.parse_args()
    args.beta = 0.0

    import bitsandbytes as bnb
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from trl.generation.vllm_client import VLLMClient

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    aliases = json.loads(args.aliases.read_text())
    label_text, label_to_rel, rel_prompt = grammar(args.mquake)
    eps = [json.loads(l) for l in args.episodes.open()]
    tok = AutoTokenizer.from_pretrained(args.model)
    reader_tok = AutoTokenizer.from_pretrained(args.reader_model)

    policy = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32).cuda()
    policy.gradient_checkpointing_enable()
    policy.config.use_cache = False
    opt = bnb.optim.AdamW8bit(policy.parameters(), lr=args.lr, betas=(0.9, 0.99), weight_decay=0.0)

    client = VLLMClient(base_url=args.writer_url, connection_timeout=900)
    client.init_communicator(device=0)
    params = [(n, p) for n, p in policy.named_parameters()]
    meta = [(n, "bfloat16", list(p.shape)) for n, p in params]

    def sync():
        client.update_named_params(meta, ((n, p.data.to(torch.bfloat16)) for n, p in params))
        client.reset_prefix_cache()

    sync()
    log = (args.out / "train_log.jsonl").open("a")

    for step in range(args.steps):
        t0 = time.time()
        batch = random.sample(eps, args.episodes_per_step)
        # 1) greedy extraction of every line by the current policy
        lines = [[(s, l) for s, sess in enumerate(ep["sessions"]) for l in range(len(sess)) if not is_header(sess[l])]
                 for ep in batch]
        prompts = {(b, s, l): line_prompt(tok, label_text, batch[b]["sessions"][s], batch[b]["sessions"][s][l], args.context)
                   for b in range(len(batch)) for s, l in lines[b]}
        keys = list(prompts)
        out = client.generate([prompts[k] for k in keys], n=1, temperature=0.0, max_tokens=args.max_new, logprobs=None)
        greedy = {k: parse_json(tok.decode(c, skip_special_tokens=True)) for k, c in zip(keys, out["completion_ids"])}
        base_items = [[greedy[(b, s, l)] for s, l in lines[b]] for b in range(len(batch))]
        # 2) line-level groups: G samples of one line, others fixed at greedy
        picks = [(b, j) for b in range(len(batch)) for j in random.sample(range(len(lines[b])), min(args.lines_per_episode, len(lines[b])))]
        sp = [prompts[(b, *lines[b][j])] for b, j in picks for _ in range(args.group)]
        out = client.generate(sp, n=1, temperature=args.temperature, top_p=1.0, max_tokens=args.max_new, logprobs=None)
        gens, mems, owners = [], [], []
        for k, (pid, cid) in enumerate(zip(out["prompt_ids"], out["completion_ids"])):
            b, j = picks[k // args.group]
            items = list(base_items[b])
            items[j] = parse_json(tok.decode(cid, skip_special_tokens=True))
            mems.append(resolve_extracted(items, label_to_rel, rel_prompt))
            owners.append(b)
            gens.append((k, pid, cid, None))
        t_roll = time.time()
        # 3) reward: reader EM of each resolved memory (identical memories scored once)
        uniq = {}
        for m, b in zip(mems, owners):
            uniq.setdefault((m, b), None)
        uk = list(uniq)
        ur = reader_rewards(args.reader_url, args.reader_model, reader_tok, [m for m, _ in uk],
                            [batch[b]["questions"] for _, b in uk], [batch[b]["hidden"]["answers"] for _, b in uk], aliases)
        uniq = dict(zip(uk, ur))
        rewards = [uniq[(m, b)] for m, b in zip(mems, owners)]
        adv = advantages(rewards, args.group, args.algo)
        t_rew = time.time()

        policy.train()
        opt.zero_grad(set_to_none=True)
        active = [g for g in gens if abs(adv[g[0]]) > 1e-8]
        total_loss, _, n_tok = pg_backward(policy, None, tok, gens, active, adv, args)
        gnorm = torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0).item() if active else 0.0
        if active:
            opt.step()
        t_bwd = time.time()
        sync()
        t_end = time.time()

        ngroups = len(picks)
        base_parse = sum(x is not None for row in base_items for x in row) / max(1, sum(map(len, base_items)))
        rec = {"step": step, "algo": args.algo, "target": "extractor", "reward_mean": sum(rewards) / len(rewards),
               "loss": total_loss, "grad_norm": gnorm, "nan": math.isnan(total_loss),
               "frac_zero_adv_groups": sum(1 for i in range(0, len(rewards), args.group)
                                           if len(set(rewards[i:i + args.group])) == 1) / ngroups,
               "active_seqs": len(active), "unique_memories": len(uk), "greedy_parse_rate": round(base_parse, 4),
               "mean_completion_tokens": sum(len(g[2]) for g in gens) / len(gens),
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
