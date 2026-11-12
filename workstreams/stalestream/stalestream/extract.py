"""Non-privileged baseline: LLM extraction + rule-based resolution ("extract_rules").

An LLM reads ONE stream line at a time and returns structured JSON:
  fact:        {"type":"fact","subject","relation","value","date","source"}
  alias:       {"type":"alias","alias","name"}
  correction:  {"type":"correction","source"}   (a source caught making a false claim)
Relations are chosen from the public list of relation types (the environment grammar),
never from hidden labels. Rules then: map aliases to names, drop every source that was
caught in a false claim, keep the latest-dated claim per (subject, relation), and render
memory within the token budget.

Also reports extraction accuracy against privileged metadata (diagnostic only).

  python -m stalestream.extract --episodes val.jsonl --mquake MQuAKE.json --out extract_val.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from .baselines import BUDGET_TOKENS, norm_date, render, truncate
from .generator import load_slots

PROMPT = """Convert the statement into JSON. Statement kinds:
1. A dated claim by a source about an entity, e.g. "As of 2021-03-05, Source-B says X's capital is Y" ->
   {{"type":"fact","subject":"X","relation":"<one label from the list>","value":"Y","date":"2021-03-05","source":"Source-B"}}
2. A note that two names refer to the same entity ->
   {{"type":"alias","alias":"<the short code or other name>","name":"<the full name>"}}
3. A verified correction saying some source's claim was false ->
   {{"type":"correction","source":"<the source whose claim was false>"}}
Copy names and values exactly as written. Write the date as YYYY-MM-DD.

Relation labels: {labels}

Statement: {line}
JSON:"""


def relation_labels(slots):
    """Public grammar: one short label per relation id, derived from its question template."""
    labels = {}
    for s in slots:
        if s["relation"] in labels:
            continue
        q = s["question"].replace(s["subject"], "X").rstrip("?")
        labels[s["relation"]] = q
    prompts = {}
    for s in slots:
        prompts.setdefault(s["relation"], s["prompt"])
    return labels, prompts


def parse_json(text: str):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
    m = re.search(r"\{.*?\}", text, flags=re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def resolve_extracted(items, label_to_rel, rel_prompt):
    aliases, flagged, claims = {}, set(), []
    for it in items:
        if not isinstance(it, dict):
            continue
        t = it.get("type")
        if t == "alias" and it.get("alias") and it.get("name"):
            aliases[str(it["alias"]).strip()] = str(it["name"]).strip()
        elif t == "correction" and it.get("source"):
            flagged.add(str(it["source"]).strip())
        elif t == "fact" and all(it.get(k) for k in ("subject", "relation", "value", "date", "source")):
            rel = label_to_rel.get(str(it["relation"]).strip())
            if rel is None:
                continue
            try:
                date = norm_date(str(it["date"]))
            except (ValueError, KeyError):
                continue
            claims.append({"subject": str(it["subject"]).strip(), "rel": rel, "value": str(it["value"]).strip(),
                           "date": date, "source": str(it["source"]).strip()})
    best = {}
    for c in claims:
        if c["source"] in flagged:
            continue
        key = (aliases.get(c["subject"], c["subject"]), c["rel"])
        if key not in best or c["date"] > best[key]["date"]:
            best[key] = c
    return truncate(render([(rel_prompt[r], s, c["value"]) for (s, r), c in best.items()]), BUDGET_TOKENS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--mquake", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--arm", default="extract_rules")
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    args = ap.parse_args()
    from vllm import LLM, SamplingParams

    slots, _, _ = load_slots(args.mquake)
    labels, rel_prompt = relation_labels(slots)
    label_to_rel = {v: k for k, v in labels.items()}
    label_text = "; ".join(f'"{v}"' for v in sorted(labels.values()))
    eps = [json.loads(l) for l in args.episodes.open()]
    llm = LLM(model=args.model, gpu_memory_utilization=args.gpu_mem, max_model_len=4096, seed=0)
    tok = llm.get_tokenizer()
    jobs = [(e, s, l) for e, ep in enumerate(eps) for s, sess in enumerate(ep["sessions"]) for l in range(len(sess))]
    prompts = [tok.apply_chat_template([{"role": "user", "content": PROMPT.format(
        labels=label_text, line=eps[e]["sessions"][s][l])}], tokenize=False, add_generation_prompt=True,
        enable_thinking=False) for e, s, l in jobs]
    outs = llm.generate(prompts, SamplingParams(temperature=0.0, max_tokens=160), use_tqdm=False)
    items = defaultdict(list)
    acc = defaultdict(int)
    for (e, s, l), o in zip(jobs, outs):
        it = parse_json(o.outputs[0].text)
        items[e].append(it)
        keep = eps[e]["hidden"]["must_keep"][s][l]
        acc["lines"] += 1
        acc["parsed"] += it is not None
        if it and it.get("type") == "fact" and len(keep) == 4:  # statement: [source, date, name, value]
            acc["facts"] += 1
            acc["fact_value_ok"] += str(it.get("value", "")).strip() == keep[3]
            acc["fact_source_ok"] += str(it.get("source", "")).strip() == keep[0]
            acc["fact_subject_ok"] += str(it.get("subject", "")).strip() == keep[2]
            try:
                acc["fact_date_ok"] += norm_date(str(it.get("date"))) == norm_date(keep[1])
            except (ValueError, KeyError):
                pass
            acc["fact_relation_valid"] += str(it.get("relation", "")).strip() in label_to_rel
    with args.out.open("w") as f:
        for e, ep in enumerate(eps):
            mem = resolve_extracted(items[e], label_to_rel, rel_prompt)
            f.write(json.dumps({"episode_id": ep["episode_id"], "arm": args.arm, "memory": mem}) + "\n")
    rates = {k: round(v / max(1, acc["facts"]), 4) for k, v in acc.items() if k.startswith("fact_") and k != "facts"}
    print(json.dumps({"lines": acc["lines"], "parse_rate": round(acc["parsed"] / acc["lines"], 4),
                      "fact_lines": acc["facts"], **rates}))


if __name__ == "__main__":
    main()
