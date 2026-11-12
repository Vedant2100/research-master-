"""Prompted LLM memory writer (non-privileged baseline; also the RL policy's prompt).

After each session the writer sees only its previous memory and that session's
statements, and emits revised memory, truncated to the token budget.

  python -m stalestream.writer --episodes test.jsonl --model Qwen/Qwen3-1.7B \
      --arm prompted_1.7b --out writer_1.7b.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .baselines import BUDGET_TOKENS, truncate

WRITER_PROMPT = """You maintain a compact memory of facts for a later reader who will see ONLY your memory, not these statements.

Rules:
- Keep only the CURRENT value of each fact: the value with the latest "as of" date, regardless of the order statements arrive in.
- Track aliases: if X is another name for Y, store facts under Y.
- Some sources may be unreliable. If Audit-Desk says a source made a false claim, distrust that source's other claims too.
- Hard limit: about {budget} tokens. One short line per fact, e.g. "Spain official language: Spanish". Remember source reliability notes if useful.

CURRENT MEMORY:
{memory}

NEW STATEMENTS (session {session}):
{statements}

Write the full revised memory now, and nothing else."""


def build_prompt(tok, memory: str, statements, session: int, budget: int = BUDGET_TOKENS) -> str:
    body = WRITER_PROMPT.format(budget=budget, memory=memory or "(empty)", session=session + 1,
                                statements="\n".join(statements))
    return tok.apply_chat_template([{"role": "user", "content": body}], tokenize=False,
                                   add_generation_prompt=True, enable_thinking=False)


def build_teacher_prompt(tok, memory: str, ep, session: int, budget: int = BUDGET_TOKENS) -> str:
    """OPSD teacher view: same instructions and memory, statements annotated with resolved dates,
    plus notes derivable from the stream so far (see hints.py). Never contains answers."""
    from .hints import teacher_notes, teacher_statements
    body = WRITER_PROMPT.format(budget=budget, memory=memory or "(empty)", session=session + 1,
                                statements="\n".join(teacher_statements(ep, session)))
    notes = teacher_notes(ep, session)
    if notes:
        body = body.replace("Write the full revised memory now",
                            "VERIFIED NOTES:\n" + notes + "\n\nWrite the full revised memory now")
    return tok.apply_chat_template([{"role": "user", "content": body}], tokenize=False,
                                   add_generation_prompt=True, enable_thinking=False)


def clean(text: str) -> str:
    import re
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def run_writer(llm, sp, episodes, budget: int = BUDGET_TOKENS, lora_request=None):
    tok = llm.get_tokenizer()
    memories = [""] * len(episodes)
    max_s = max(len(ep["sessions"]) for ep in episodes)
    for s in range(max_s):
        idx = [i for i, ep in enumerate(episodes) if s < len(ep["sessions"])]
        prompts = [build_prompt(tok, memories[i], episodes[i]["sessions"][s], s, budget) for i in idx]
        outs = llm.generate(prompts, sp, use_tqdm=False, lora_request=lora_request)
        for i, o in zip(idx, outs):
            memories[i] = truncate(clean(o.outputs[0].text), budget)
    return memories


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--arm", default="prompted_1.7b")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--lora", type=Path, default=None, help="trained LoRA adapter dir")
    ap.add_argument("--lora-r", type=int, default=16)
    ap.add_argument("--gpu-mem", type=float, default=0.85)
    ap.add_argument("--max-len", type=int, default=4096)
    args = ap.parse_args()
    from vllm import LLM, SamplingParams
    eps = [json.loads(l) for l in args.episodes.open()]
    if args.limit:
        eps = eps[: args.limit]
    lora_kw = dict(enable_lora=True, max_lora_rank=args.lora_r, max_loras=1) if args.lora else {}
    llm = LLM(model=args.model, gpu_memory_utilization=args.gpu_mem, max_model_len=args.max_len, seed=0, **lora_kw)
    sp = SamplingParams(temperature=0.0, max_tokens=320)
    lora = None
    if args.lora:
        from vllm.lora.request import LoRARequest
        lora = LoRARequest("eval", 1, str(args.lora))
    mems = run_writer(llm, sp, eps, lora_request=lora)
    with args.out.open("w") as f:
        for ep, m in zip(eps, mems):
            f.write(json.dumps({"episode_id": ep["episode_id"], "arm": args.arm, "memory": m}) + "\n")


if __name__ == "__main__":
    main()
