"""Sample bank for RFT and DPO (HANDOFF item 8), with shared-state candidate groups.

For each 2-session training episode, two shared states are built from the BASE writer:
  s1: empty memory + session-1 statements. G candidates are sampled; each is finished
      greedily through session 2 so it gets a final memory to score.
  s2: one session-1 candidate's memory (chosen at random) + session-2 statements. G candidates
      are sampled; each candidate IS the final memory.
Candidates within a state share the exact prompt, so DPO pairs and RFT targets are well defined.
Sampling budget: episodes × 2 states × G candidates (600 × 2 × 8 = 9,600, matching GRPO's
300 steps × 32 trajectories).

  python -m stalestream.bank gen   --episodes train_2s.jsonl --n 600 --out bank_raw.jsonl     # writer GPU
  python -m stalestream.bank score --bank bank_raw.jsonl --episodes train_2s.jsonl --aliases value_aliases.json \
      --mquake MQuAKE.json --out bank_scored.jsonl                                             # reader GPU
  python -m stalestream.bank build --bank bank_scored.jsonl --out-dir bank/                    # CPU
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .baselines import BUDGET_TOKENS, truncate
from .writer import build_prompt, clean


def gen(args):
    from vllm import LLM, SamplingParams
    eps = [json.loads(l) for l in args.episodes.open()]
    rng = random.Random(args.seed)
    rng.shuffle(eps)
    eps = [e for e in eps if len(e["sessions"]) == 2][: args.n]
    llm = LLM(model=args.model, gpu_memory_utilization=0.85, max_model_len=4096, seed=args.seed)
    tok = llm.get_tokenizer()
    sample = SamplingParams(n=args.group, temperature=1.0, top_p=1.0, max_tokens=args.max_new, seed=None)
    greedy = SamplingParams(temperature=0.0, max_tokens=args.max_new)

    p1 = [build_prompt(tok, "", ep["sessions"][0], 0) for ep in eps]
    c1 = [[clean(o.text) for o in out.outputs] for out in llm.generate(p1, sample, use_tqdm=False)]
    # finish every s1 candidate greedily through session 2
    fin_prompts = [build_prompt(tok, truncate(c, BUDGET_TOKENS), ep["sessions"][1], 1) for ep, cs in zip(eps, c1) for c in cs]
    fin = [clean(o.outputs[0].text) for o in llm.generate(fin_prompts, greedy, use_tqdm=False)]
    # s2 shared state: a random s1 candidate's (truncated) memory
    shared = [truncate(cs[rng.randrange(len(cs))], BUDGET_TOKENS) for cs in c1]
    p2 = [build_prompt(tok, m, ep["sessions"][1], 1) for ep, m in zip(eps, shared)]
    c2 = [[clean(o.text) for o in out.outputs] for out in llm.generate(p2, sample, use_tqdm=False)]

    with args.out.open("w") as f:
        k = 0
        for ep, pr, cs, pr2, cs2 in zip(eps, p1, c1, p2, c2):
            finals = fin[k:k + len(cs)]
            k += len(cs)
            f.write(json.dumps({"episode_id": ep["episode_id"], "state": "s1", "prompt": pr, "candidates": cs,
                                "finals": [truncate(x, BUDGET_TOKENS) for x in finals]}) + "\n")
            f.write(json.dumps({"episode_id": ep["episode_id"], "state": "s2", "prompt": pr2, "candidates": cs2,
                                "finals": [truncate(x, BUDGET_TOKENS) for x in cs2]}) + "\n")
    print(json.dumps({"episodes": len(eps), "states": 2 * len(eps), "samples": 2 * len(eps) * args.group}))


def score(args):
    from .reader import Reader, score as em
    eps = {json.loads(l)["episode_id"]: json.loads(l) for l in args.episodes.open()}
    aliases = json.loads(args.aliases.read_text())
    rows = [json.loads(l) for l in args.bank.open()]
    mems, qs, idx = [], [], []
    for r_i, r in enumerate(rows):
        for c_i, m in enumerate(r["finals"]):
            mems.append(m)
            qs.append(eps[r["episode_id"]]["questions"])
            idx.append((r_i, c_i))
    preds = Reader(args.reader_model).answer(mems, qs)
    for r in rows:
        r["rewards"] = [None] * len(r["finals"])
    for (r_i, c_i), p in zip(idx, preds):
        rows[r_i]["rewards"][c_i] = em(p, eps[rows[r_i]["episode_id"]]["hidden"]["answers"], aliases)[0]
    with args.out.open("w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    allr = [x for r in rows for x in r["rewards"]]
    print(json.dumps({"scored": len(allr), "mean_reward": round(sum(allr) / len(allr), 4)}))


def build(args):
    rows = [json.loads(l) for l in args.bank.open()]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rft, dpo = [], []
    for r in rows:
        rw = r["rewards"]
        best = max(range(len(rw)), key=lambda i: rw[i])
        worst = min(range(len(rw)), key=lambda i: rw[i])
        if rw[best] > 0 and rw[best] >= sum(rw) / len(rw):
            rft.append({"prompt": r["prompt"], "completion": r["candidates"][best], "reward": rw[best],
                        "episode_id": r["episode_id"], "state": r["state"]})
        if rw[best] - rw[worst] >= args.min_gap - 1e-9:
            dpo.append({"prompt": r["prompt"], "chosen": r["candidates"][best], "rejected": r["candidates"][worst],
                        "gap": rw[best] - rw[worst], "episode_id": r["episode_id"], "state": r["state"]})
    for name, data in [("rft.jsonl", rft), ("dpo.jsonl", dpo)]:
        with (args.out_dir / name).open("w") as f:
            for d in data:
                f.write(json.dumps(d) + "\n")
    print(json.dumps({"states": len(rows), "rft_examples": len(rft), "dpo_pairs": len(dpo),
                      "mean_rft_reward": round(sum(d["reward"] for d in rft) / max(1, len(rft)), 4),
                      "mean_dpo_gap": round(sum(d["gap"] for d in dpo) / max(1, len(dpo)), 4)}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--episodes", type=Path, required=True)
    g.add_argument("--out", type=Path, required=True)
    g.add_argument("--n", type=int, default=600)
    g.add_argument("--group", type=int, default=8)
    g.add_argument("--model", default="Qwen/Qwen3-1.7B")
    g.add_argument("--max-new", type=int, default=256)
    g.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("score")
    s.add_argument("--bank", type=Path, required=True)
    s.add_argument("--episodes", type=Path, required=True)
    s.add_argument("--aliases", type=Path, required=True)
    s.add_argument("--mquake", type=Path, required=False)
    s.add_argument("--reader-model", default="Qwen/Qwen3-4B")
    s.add_argument("--out", type=Path, required=True)
    b = sub.add_parser("build")
    b.add_argument("--bank", type=Path, required=True)
    b.add_argument("--out-dir", type=Path, required=True)
    b.add_argument("--min-gap", type=float, default=2 / 6)
    args = ap.parse_args()
    {"gen": gen, "score": score, "build": build}[args.cmd](args)


if __name__ == "__main__":
    main()
