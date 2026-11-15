"""Is relative / cross-referenced date resolution within reach of RL? (val split, diagnostic only)

For every relative_date and xref_date statement line, sample N extractions at temperature 1 (plus one
greedy) with the extractor prompt and report, per kind: greedy exact-date rate, per-sample exact rate,
pass@N (any sample exact), and the same within +/-30 days. If pass@N is ~0 the policy never produces a
correct date, so a policy-gradient method has nothing to reinforce on these lines.

  python -m stalestream.probe_dates --episodes val.jsonl --mquake MQ.json --model M --context session
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

from .baselines import norm_date
from .dates import gold_dates
from .extract import grammar, line_prompt, parse_json


def date_of(text):
    it = parse_json(text)
    try:
        return dt.date.fromisoformat(norm_date(str(it.get("date")))) if isinstance(it, dict) else None
    except (ValueError, KeyError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--mquake", type=Path, required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--context", choices=["header", "session"], default="session")
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--max-lines", type=int, default=1500)
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    from vllm import LLM, SamplingParams

    label_text, _, _ = grammar(args.mquake)
    jobs = []
    for ep in map(json.loads, args.episodes.open()):
        for (s, l), (gold, kind) in gold_dates(ep).items():
            if kind != "absolute_date":
                jobs.append((ep["sessions"][s], ep["sessions"][s][l], dt.date.fromisoformat(gold), kind))
    jobs = jobs[: args.max_lines]
    llm = LLM(model=args.model, gpu_memory_utilization=args.gpu_mem, max_model_len=4096, seed=0,
              enable_prefix_caching=True)
    tok = llm.get_tokenizer()
    prompts = [line_prompt(tok, label_text, sess, line, args.context) for sess, line, _, _ in jobs]
    greedy = llm.generate(prompts, SamplingParams(temperature=0.0, max_tokens=192), use_tqdm=False)
    samp = llm.generate(prompts, SamplingParams(n=args.n, temperature=1.0, max_tokens=192), use_tqdm=False)
    acc = defaultdict(lambda: defaultdict(float))
    for (_, _, gold, kind), g, o in zip(jobs, greedy, samp):
        ds = [date_of(x.text) for x in o.outputs]
        err = [abs((d - gold).days) if d else 10**6 for d in ds]
        gd = date_of(g.outputs[0].text)
        for k in (kind, "all"):
            a = acc[k]
            a["lines"] += 1
            a["greedy_exact"] += gd == gold
            a["sample_exact"] += sum(e == 0 for e in err) / len(err)
            a["pass_exact"] += any(e == 0 for e in err)
            a["sample_30d"] += sum(e <= 30 for e in err) / len(err)
            a["pass_30d"] += any(e <= 30 for e in err)
    res = {k: {m: (round(v / a["lines"], 4) if m != "lines" else int(v)) for m, v in a.items()} for k, a in acc.items()}
    out = {"model": args.model, "context": args.context, "n": args.n, **res}
    print(json.dumps(out))
    if args.out:
        args.out.write_text(json.dumps(out) + "\n")


if __name__ == "__main__":
    main()
