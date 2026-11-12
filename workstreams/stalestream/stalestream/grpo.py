"""Multi-session GRPO / RLOO for the memory writer (LoRA on Qwen3-1.7B).

One trajectory = the writer's memory rewrites over all sessions of an episode. Reward
= frozen reader's exact match on the six questions from the final memory. The
episode-level advantage is applied to every writer generation in the trajectory
(credit spread across sessions). One gradient step per batch, so this is on-policy
and the PPO ratio is 1 (no clipping needed); beta = 0 (no KL) in this version.

  advantages: grpo -> (r - mean_g) / (std_g + 1e-4)     rloo -> r - mean_{others}

Layout: rollouts with vLLM + LoRA on the writer GPU, gradients with HF+PEFT on the
same GPU, and the reader as an OpenAI-compatible `vllm serve` on another GPU:

  CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --max-model-len 2048
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo --episodes train_2s.jsonl \
      --aliases value_aliases.json --steps 20 --algo grpo --out runs/grpo_timing
"""
from __future__ import annotations

import argparse
import json
import math
import random
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
import torch

from .baselines import BUDGET_TOKENS, truncate
from .reader import parse_answers, reader_prompts, score
from .writer import build_prompt, clean


def reader_rewards(url, model, tok, memories, question_lists, golds, aliases):
    prompts = reader_prompts(tok, memories, question_lists)

    def call(chunk):
        r = requests.post(f"{url}/v1/completions", timeout=600, json={
            "model": model, "prompt": chunk, "temperature": 0.0, "max_tokens": 128})
        r.raise_for_status()
        return [c["text"] for c in sorted(r.json()["choices"], key=lambda c: c["index"])]

    chunks = [prompts[i:i + 32] for i in range(0, len(prompts), 32)]
    with ThreadPoolExecutor(4) as ex:
        texts = [t for out in ex.map(call, chunks) for t in out]
    return [score(parse_answers(t, len(q)), g, aliases)[0] for t, q, g in zip(texts, question_lists, golds)]


def advantages(rewards, group, algo):
    out = []
    for i in range(0, len(rewards), group):
        g = rewards[i:i + group]
        mean = sum(g) / len(g)
        if algo == "grpo":
            std = math.sqrt(sum((x - mean) ** 2 for x in g) / len(g))
            out += [(x - mean) / (std + 1e-4) for x in g]
        else:
            out += [x - (sum(g) - x) / (len(g) - 1) for x in g]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--aliases", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--reader-url", default="http://127.0.0.1:8401")
    ap.add_argument("--reader-model", default="Qwen/Qwen3-4B")
    ap.add_argument("--algo", choices=["grpo", "rloo"], default="grpo")
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--episodes-per-step", type=int, default=4)
    ap.add_argument("--group", type=int, default=8)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--max-new", type=int, default=256)
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--micro-batch", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    from peft import LoraConfig, get_peft_model
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from vllm import LLM, SamplingParams
    from vllm.lora.request import LoRARequest

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    aliases = json.loads(args.aliases.read_text())
    eps = [json.loads(l) for l in args.episodes.open()]
    reader_tok = AutoTokenizer.from_pretrained(args.reader_model)

    llm = LLM(model=args.model, enable_lora=True, max_lora_rank=args.lora_r, max_loras=1,
              gpu_memory_utilization=0.35, max_model_len=4096, seed=args.seed)
    tok = llm.get_tokenizer()
    policy = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.bfloat16).cuda()
    policy.gradient_checkpointing_enable()
    policy.enable_input_require_grads()
    policy = get_peft_model(policy, LoraConfig(r=args.lora_r, lora_alpha=2 * args.lora_r, lora_dropout=0.0,
                                               target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                                                               "gate_proj", "up_proj", "down_proj"]))
    opt = torch.optim.AdamW([p for p in policy.parameters() if p.requires_grad], lr=args.lr)
    sp = SamplingParams(temperature=args.temperature, top_p=1.0, max_tokens=args.max_new)  # no per-request seed: it would make all G samples identical
    log = (args.out / "train_log.jsonl").open("a")

    for step in range(args.steps):
        t0 = time.time()
        adapter = args.out / "adapter_current"
        policy.save_pretrained(adapter)
        lora = LoRARequest(f"s{step}", step + 1, str(adapter))
        batch = random.sample(eps, args.episodes_per_step)
        trajs = [ep for ep in batch for _ in range(args.group)]
        memories = [""] * len(trajs)
        gens = []  # (traj index, prompt text, completion token ids)
        for s in range(max(len(ep["sessions"]) for ep in batch)):
            idx = [i for i, ep in enumerate(trajs) if s < len(ep["sessions"])]
            prompts = [build_prompt(tok, memories[i], trajs[i]["sessions"][s], s) for i in idx]
            outs = llm.generate(prompts, sp, lora_request=lora, use_tqdm=False)
            for i, p, o in zip(idx, prompts, outs):
                gens.append((i, p, list(o.outputs[0].token_ids)))
                memories[i] = truncate(clean(o.outputs[0].text), BUDGET_TOKENS)
        t_roll = time.time()

        rewards = reader_rewards(args.reader_url, args.reader_model, reader_tok, memories,
                                 [ep["questions"] for ep in trajs], [ep["hidden"]["answers"] for ep in trajs], aliases)
        adv = advantages(rewards, args.group, args.algo)
        t_rew = time.time()

        policy.train()
        opt.zero_grad(set_to_none=True)
        active = [g for g in gens if abs(adv[g[0]]) > 1e-8]
        total_loss = 0.0
        for k in range(0, len(active), args.micro_batch):
            mb = active[k:k + args.micro_batch]
            seqs, masks = [], []
            for i, p, comp in mb:
                pid = tok(p, add_special_tokens=False)["input_ids"]
                seqs.append(pid + comp)
                masks.append([0] * len(pid) + [1] * len(comp))
            L = max(map(len, seqs))
            ids = torch.full((len(mb), L), tok.pad_token_id, dtype=torch.long)
            att = torch.zeros((len(mb), L), dtype=torch.long)
            cm = torch.zeros((len(mb), L), dtype=torch.float)
            for j, (sq, m) in enumerate(zip(seqs, masks)):
                ids[j, :len(sq)] = torch.tensor(sq)
                att[j, :len(sq)] = 1
                cm[j, :len(sq)] = torch.tensor(m, dtype=torch.float)
            ids, att, cm = ids.cuda(), att.cuda(), cm.cuda()
            # Only completion positions are scored; slice before the vocab-wide softmax.
            start = min(m.index(1) for m in masks) - 1
            logits = policy(input_ids=ids, attention_mask=att, logits_to_keep=L - start).logits[:, :-1]
            tgt = ids[:, start + 1:]
            lp = logits.gather(-1, tgt[..., None]).squeeze(-1).float() - torch.logsumexp(logits.float(), -1)
            m = cm[:, start + 1:]
            a = torch.tensor([adv[i] for i, _, _ in mb], device=lp.device)
            # Dr.GRPO-style constant normalizer (max_new) instead of per-sequence length.
            per_seq = (lp * m).sum(-1) / args.max_new
            loss = -(a * per_seq).sum() / max(1, len(gens))
            loss.backward()
            total_loss += loss.item()
            del logits, lp
        gnorm = torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0).item()
        opt.step()
        t_end = time.time()

        rec = {"step": step, "algo": args.algo, "reward_mean": sum(rewards) / len(rewards),
               "reward_std": float(torch.tensor(rewards).std()), "loss": total_loss, "grad_norm": gnorm,
               "frac_zero_adv_groups": sum(1 for i in range(0, len(rewards), args.group)
                                           if len(set(rewards[i:i + args.group])) == 1) / args.episodes_per_step,
               "mean_completion_tokens": sum(len(g[2]) for g in gens) / len(gens),
               "t_rollout": round(t_roll - t0, 2), "t_reward": round(t_rew - t_roll, 2),
               "t_backward": round(t_end - t_rew, 2), "t_step": round(t_end - t0, 2)}
        log.write(json.dumps(rec) + "\n")
        log.flush()
        print(json.dumps(rec), flush=True)
    policy.save_pretrained(args.out / "adapter_final")


if __name__ == "__main__":
    main()
