"""v1 language difficulty: LLM paraphrase of every stream line, label strings preserved.

Each line is rewritten by an LLM into varied natural wording. A paraphrase is accepted
only if every must_keep string (source, date surface form, subject or alias, value)
appears verbatim and no other episode-value leaks in; otherwise it retries, then falls
back to the template line (the fallback rate is reported, since fallbacks stay
regex-parseable). must_keep comes from the generator's privileged metadata.

  python -m stalestream.paraphrase --episodes raw/test.jsonl --out v1/test.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

PROMPT = """Rewrite the statement below in different, natural wording, as it might appear in a news brief, chat log, or analyst note. Vary sentence structure; do not just reorder it.

You MUST copy each of these strings exactly, character for character: {keep}
Do not add any facts, names, places, or dates. Output only the rewritten statement, one sentence.

Statement: {line}"""

STYLES = ["a terse wire-service brief", "a casual chat message", "an analyst's note", "a formal report sentence",
          "a headline-style fragment followed by detail"]


NEGATION = re.compile(r"\b(false|incorrect|wrong|inaccurate|untrue|not true|erroneous|mistaken|debunked)\b", re.I)


def accept(text: str, keep, forbidden) -> bool:
    if not text or "\n" in text.strip() or len(text) > 400:
        return False
    if any(k not in text for k in keep):
        return False
    if any(f in text for f in forbidden):
        return False
    if "Audit-Desk" in keep and not NEGATION.search(text):  # audit must still say the claim is false
        return False
    if "Audit-Desk" not in keep and NEGATION.search(text):  # ordinary claims must not be negated
        return False
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--tries", type=int, default=3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()
    from vllm import LLM, SamplingParams

    eps = [json.loads(l) for l in args.episodes.open()]
    if args.limit:
        eps = eps[: args.limit]
    rng = random.Random(args.seed)
    llm = LLM(model=args.model, gpu_memory_utilization=0.85, max_model_len=2048, seed=args.seed)
    tok = llm.get_tokenizer()
    sp = SamplingParams(temperature=0.9, top_p=0.95, max_tokens=120)

    # jobs: (ep index, session, line index)
    jobs, done = [], {}
    for e_i, ep in enumerate(eps):
        values = {t["value"] for t in ep["hidden"]["truth"].values()}
        for s_i, sess in enumerate(ep["sessions"]):
            for l_i, line in enumerate(sess):
                keep = ep["hidden"]["must_keep"][s_i][l_i]
                forbidden = [v for v in values if v not in line and not any(v in k for k in keep)]
                jobs.append((e_i, s_i, l_i, line, keep, forbidden))
    pending = list(range(len(jobs)))
    for attempt in range(args.tries):
        if not pending:
            break
        prompts = []
        for j in pending:
            _, _, _, line, keep, _ = jobs[j]
            body = PROMPT.format(keep="; ".join(f'"{k}"' for k in keep), line=line)
            body += f"\nWrite it as {rng.choice(STYLES)}."
            prompts.append(tok.apply_chat_template([{"role": "user", "content": body}], tokenize=False,
                                                   add_generation_prompt=True, enable_thinking=False))
        outs = llm.generate(prompts, sp, use_tqdm=False)
        still = []
        for j, o in zip(pending, outs):
            text = re.sub(r"<think>.*?</think>", "", o.outputs[0].text, flags=re.S).strip().strip('*').strip().strip('"')
            if accept(text, jobs[j][4], jobs[j][5]):
                done[j] = text
            else:
                still.append(j)
        print(json.dumps({"attempt": attempt, "accepted_total": len(done), "remaining": len(still)}), flush=True)
        pending = still

    for j, (e_i, s_i, l_i, line, _, _) in enumerate(jobs):
        eps[e_i]["sessions"][s_i][l_i] = done.get(j, line)
        eps[e_i]["hidden"].setdefault("paraphrased", [[False] * len(s) for s in eps[e_i]["sessions"]])
        eps[e_i]["hidden"]["paraphrased"][s_i][l_i] = j in done
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for ep in eps:
            f.write(json.dumps(ep) + "\n")
    print(json.dumps({"lines": len(jobs), "paraphrased": len(done), "fallback_rate": round(1 - len(done) / len(jobs), 4)}))


if __name__ == "__main__":
    main()
