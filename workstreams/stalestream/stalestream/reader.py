"""Frozen reader: answers the six questions from final memory only, in one call.

Writes one row per (episode, arm) in the headroom_gate.py format, plus per-question
detail. Memories for LLM-writer arms come from --memories JSONL rows
{"episode_id", "arm", "memory"}; rule arms are computed in-process.

  python -m stalestream.reader --episodes test.jsonl --aliases value_aliases.json \
      --arms oracle no_memory write_all newest_wins symbolic --memories writer.jsonl \
      --out eval.jsonl
"""
from __future__ import annotations

import argparse
import json
import re
import string
from pathlib import Path

from .baselines import RULE_ARMS, Grammar, arm_memory, n_tokens

READER = "Qwen/Qwen3-4B"
PROMPT = """You answer questions using ONLY the memory notes below. The notes may describe a fictional world; trust the notes over your own knowledge. If the notes do not contain the answer, give your best guess.

MEMORY:
{memory}

QUESTIONS:
{questions}

Reply with a JSON list of exactly {n} short answers (just the entity name for each), in order, and nothing else."""


def normalize(s: str) -> str:
    s = s.lower().strip()
    s = "".join(ch for ch in s if ch not in string.punctuation)
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    return " ".join(s.split())


def exact_match(pred: str, gold: str, aliases: dict) -> bool:
    p = normalize(pred)
    return any(p == normalize(g) for g in [gold, *aliases.get(gold, [])])


def parse_answers(text: str, n: int):
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
    m = re.search(r"\[.*\]", text, flags=re.S)
    if m:
        try:
            out = json.loads(m.group(0))
            if isinstance(out, list):
                out = [str(x) for x in out]
                return (out + [""] * n)[:n]
        except json.JSONDecodeError:
            pass
    lines = [re.sub(r"^\s*\d+[.)]\s*", "", l).strip() for l in text.splitlines() if l.strip()]
    return (lines + [""] * n)[:n]


def reader_prompts(tok, memories, question_lists):
    out = []
    for mem, qs in zip(memories, question_lists):
        body = PROMPT.format(memory=mem or "(empty)", n=len(qs),
                             questions="\n".join(f"{i + 1}. {q}" for i, q in enumerate(qs)))
        out.append(tok.apply_chat_template([{"role": "user", "content": body}], tokenize=False,
                                           add_generation_prompt=True, enable_thinking=False))
    return out


class Reader:
    def __init__(self, model: str = READER, gpu_mem: float = 0.85, max_len: int = 2048):
        from vllm import LLM, SamplingParams
        self.llm = LLM(model=model, gpu_memory_utilization=gpu_mem, max_model_len=max_len, seed=0)
        self.sp = SamplingParams(temperature=0.0, max_tokens=128)
        self.tok = self.llm.get_tokenizer()

    def prompts(self, memories, question_lists):
        return reader_prompts(self.tok, memories, question_lists)

    def answer(self, memories, question_lists):
        outs = self.llm.generate(self.prompts(memories, question_lists), self.sp, use_tqdm=False)
        return [parse_answers(o.outputs[0].text, len(qs)) for o, qs in zip(outs, question_lists)]


def score(preds, golds, aliases):
    hits = [exact_match(p, g, aliases) for p, g in zip(preds, golds)]
    return sum(hits) / len(hits), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--aliases", type=Path, required=True)
    ap.add_argument("--mquake", type=Path, required=True, help="for the public relation grammar")
    ap.add_argument("--arms", nargs="+", default=RULE_ARMS)
    ap.add_argument("--memories", type=Path, action="append", default=[])
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--model", default=READER)
    args = ap.parse_args()

    from .generator import load_slots
    slots, _, _ = load_slots(args.mquake)
    grammar = Grammar([s["prompt"] for s in slots])
    aliases = json.loads(args.aliases.read_text())
    eps = [json.loads(l) for l in args.episodes.open()]
    if args.limit:
        eps = eps[: args.limit]
    ext = {}
    for path in args.memories:
        for l in path.open():
            r = json.loads(l)
            ext[(r["episode_id"], r["arm"])] = r["memory"]

    jobs = []
    for arm in args.arms:
        for ep in eps:
            mem = ext[(ep["episode_id"], arm)] if arm not in RULE_ARMS else arm_memory(arm, ep, grammar)
            jobs.append((ep, arm, mem))
    reader = Reader(args.model)
    preds = reader.answer([m for _, _, m in jobs], [ep["questions"] for ep, _, _ in jobs])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w") as f:
        for (ep, arm, mem), p in zip(jobs, preds):
            em, hits = score(p, ep["hidden"]["answers"], aliases)
            f.write(json.dumps({"episode_id": ep["episode_id"], "arm": arm, "qa_exact_match": em,
                                "hits": hits, "preds": p, "gold": ep["hidden"]["answers"],
                                "memory_tokens": n_tokens(mem), "memory": mem}) + "\n")
    summary = {}
    for (ep, arm, _), p in zip(jobs, preds):
        summary.setdefault(arm, []).append(score(p, ep["hidden"]["answers"], aliases)[0])
    print(json.dumps({a: round(sum(v) / len(v), 4) for a, v in summary.items()}, indent=2))


if __name__ == "__main__":
    main()
