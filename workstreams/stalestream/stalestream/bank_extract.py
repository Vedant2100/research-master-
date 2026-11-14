"""Sample bank for RFT / DPO on the EXTRACTOR, with the same line-level groups as grpo_extract.py.

For each training episode, the BASE extractor greedily extracts every line; then, for every line,
G alternative extractions of that one line are sampled while the other lines stay greedy. Each
alternative is resolved by the rules and scored by the reader (episode EM). A group is the G samples of
one line, so all candidates share the exact prompt. Budget matches one GRPO-extractor seed:
800 episodes (200 steps x 4) x all lines x G = 8.

  python -m stalestream.bank_extract gen   --episodes train_2s.jsonl --mquake MQ.json --out raw.jsonl     # GPU
  python -m stalestream.bank_extract score --bank raw.jsonl --episodes train_2s.jsonl --mquake MQ.json \
      --aliases value_aliases.json --out scored.jsonl                                                    # GPU
  python -m stalestream.bank build --bank scored.jsonl --out-dir bank/ --min-gap 0.16 --strict           # CPU
"""
from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from .extract import grammar, is_header, line_prompt, parse_json, resolve_extracted


def gen(args):
    from vllm import LLM, SamplingParams
    label_text, _, _ = grammar(args.mquake)
    eps = [json.loads(l) for l in args.episodes.open()]
    random.Random(args.seed).shuffle(eps)
    eps = eps[: args.n]
    llm = LLM(model=args.model, gpu_memory_utilization=0.85, max_model_len=4096, seed=args.seed,
              enable_prefix_caching=True)
    tok = llm.get_tokenizer()
    jobs = [(e, s, l) for e, ep in enumerate(eps) for s, sess in enumerate(ep["sessions"])
            for l in range(len(sess)) if not is_header(sess[l])]
    prompts = [line_prompt(tok, label_text, eps[e]["sessions"][s], eps[e]["sessions"][s][l], args.context)
               for e, s, l in jobs]
    greedy = [o.outputs[0].text for o in llm.generate(prompts, SamplingParams(temperature=0.0, max_tokens=args.max_new), use_tqdm=False)]
    samp = llm.generate(prompts, SamplingParams(n=args.group, temperature=1.0, top_p=1.0, max_tokens=args.max_new), use_tqdm=False)
    with args.out.open("w") as f:
        for (e, s, l), p, g, o in zip(jobs, prompts, greedy, samp):
            f.write(json.dumps({"episode_id": eps[e]["episode_id"], "line": [s, l], "prompt": p, "greedy": g,
                                "candidates": [x.text for x in o.outputs]}) + "\n")
    print(json.dumps({"episodes": len(eps), "groups": len(jobs), "samples": len(jobs) * args.group}))


def score(args):
    from .reader import Reader, score as em
    _, label_to_rel, rel_prompt = grammar(args.mquake)
    eps = {json.loads(l)["episode_id"]: json.loads(l) for l in args.episodes.open()}
    aliases = json.loads(args.aliases.read_text())
    rows = [json.loads(l) for l in args.bank.open()]
    by_ep = {}
    for i, r in enumerate(rows):
        by_ep.setdefault(r["episode_id"], []).append(i)
    base = {e: [parse_json(rows[i]["greedy"]) for i in idx] for e, idx in by_ep.items()}
    mems, keys = {}, []
    for e, idx in by_ep.items():
        for j, i in enumerate(idx):
            ks = []
            for c in rows[i]["candidates"]:
                items = list(base[e])
                items[j] = parse_json(c)
                m = resolve_extracted(items, label_to_rel, rel_prompt)
                mems.setdefault((e, m), None)
                ks.append((e, m))
            keys.append((i, ks))
    uk = list(mems)
    preds = Reader(args.reader_model).answer([m for _, m in uk], [eps[e]["questions"] for e, _ in uk])
    val = {k: em(p, eps[k[0]]["hidden"]["answers"], aliases)[0] for k, p in zip(uk, preds)}
    with args.out.open("w") as f:
        for i, ks in keys:
            r = rows[i]
            r["rewards"] = [val[k] for k in ks]
            r["finals"] = None
            f.write(json.dumps(r) + "\n")
    print(json.dumps({"groups": len(keys), "unique_memories": len(uk),
                      "frac_groups_with_variance": round(sum(len(set(val[k] for k in ks)) > 1 for _, ks in keys) / len(keys), 4)}))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("gen")
    g.add_argument("--episodes", type=Path, required=True)
    g.add_argument("--mquake", type=Path, required=True)
    g.add_argument("--out", type=Path, required=True)
    g.add_argument("--n", type=int, default=800)
    g.add_argument("--group", type=int, default=8)
    g.add_argument("--model", default="Qwen/Qwen3-1.7B")
    g.add_argument("--context", choices=["header", "session"], default="header")
    g.add_argument("--max-new", type=int, default=192)
    g.add_argument("--seed", type=int, default=0)
    s = sub.add_parser("score")
    s.add_argument("--bank", type=Path, required=True)
    s.add_argument("--episodes", type=Path, required=True)
    s.add_argument("--mquake", type=Path, required=True)
    s.add_argument("--aliases", type=Path, required=True)
    s.add_argument("--reader-model", default="Qwen/Qwen3-4B")
    s.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    {"gen": gen, "score": score}[args.cmd](args)


if __name__ == "__main__":
    main()
