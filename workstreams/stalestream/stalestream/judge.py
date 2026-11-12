"""Paraphrase faithfulness check: does each paraphrase state the same fact as its template line?

Samples N paraphrased lines (raw template vs paraphrase) and asks a judge model, ideally a
different model from the paraphraser (default Qwen3-32B-AWQ), for a YES/NO verdict. Reports the
unfaithful rate with a 95% Wilson interval and writes the flagged pairs for manual review.

  python -m stalestream.judge --raw raw/test.jsonl --para v2/test.jsonl --n 400 --out judge_test.jsonl
"""
from __future__ import annotations

import argparse
import json
import math
import random
import re
from pathlib import Path

PROMPT = """Two sentences are below. Answer YES if the SECOND states exactly the same information as the FIRST: the same entity, the same relationship (e.g. "died in" is not "was born in"), the same value, the same date, the same source, and the same truth (a claim and a correction of it are different). Wording may differ. Otherwise answer NO.

FIRST: {a}
SECOND: {b}

Answer YES or NO only."""


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return round(max(0, c - h), 4), round(min(1, c + h), 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw", type=Path, required=True)
    ap.add_argument("--para", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--model", default="Qwen/Qwen3-32B-AWQ")
    ap.add_argument("--gpu-mem", type=float, default=0.92)
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    from vllm import LLM, SamplingParams

    raw = [json.loads(l) for l in args.raw.open()]
    par = [json.loads(l) for l in args.para.open()]
    pairs = [(r, p) for a, b in zip(raw, par)
             for sr, sp, fl in zip(a["sessions"], b["sessions"], b["hidden"]["paraphrased"])
             for r, p, f in zip(sr, sp, fl) if f]
    random.Random(args.seed).shuffle(pairs)
    pairs = pairs[: args.n]
    llm = LLM(model=args.model, gpu_memory_utilization=args.gpu_mem, max_model_len=1024, seed=0)
    tok = llm.get_tokenizer()
    prompts = [tok.apply_chat_template([{"role": "user", "content": PROMPT.format(a=a, b=b)}], tokenize=False,
                                       add_generation_prompt=True, enable_thinking=False) for a, b in pairs]
    outs = llm.generate(prompts, SamplingParams(temperature=0.0, max_tokens=4), use_tqdm=False)
    verdicts = [re.sub(r"<think>.*?</think>", "", o.outputs[0].text, flags=re.S).strip().upper() for o in outs]
    bad = [(a, b, v) for (a, b), v in zip(pairs, verdicts) if not v.startswith("YES")]
    with args.out.open("w") as f:
        for a, b, v in bad:
            f.write(json.dumps({"raw": a, "paraphrase": b, "verdict": v}) + "\n")
    print(json.dumps({"judged": len(pairs), "unfaithful": len(bad), "rate": round(len(bad) / max(1, len(pairs)), 4),
                      "wilson95": wilson(len(bad), len(pairs)), "judge": args.model}))


if __name__ == "__main__":
    main()
