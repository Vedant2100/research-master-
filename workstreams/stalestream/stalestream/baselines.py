"""Non-LLM memory arms: oracle (privileged), no_memory, write_all, newest_wins, symbolic.

Each arm maps an episode to a final memory string. Only `oracle` reads `hidden`; the
others see only the session text plus the environment grammar (the public relation
phrasings from MQuAKE), the same knowledge a rule-writer would have.
"""
from __future__ import annotations

import re
from functools import lru_cache

BUDGET_TOKENS = 160
TOKENIZER = "Qwen/Qwen3-1.7B"

_MON = r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\.?"
# Every absolute date surface form the generator can emit (v0: ISO; v1: mixed).
DATE = (r"(\d{4}-\d{2}-\d{2}|\d{4}/\d{2}/\d{2}|" + _MON + r" \d{1,2}, \d{4}|\d{1,2} " + _MON + r" \d{4})")
_MONTHS = {m: i + 1 for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"])}


def norm_date(text: str) -> str:
    """Normalize any supported surface form to ISO so dates compare correctly."""
    t = text.strip()
    m = re.fullmatch(r"(\d{4})[-/](\d{2})[-/](\d{2})", t)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.fullmatch(r"([A-Za-z]+)\.? (\d{1,2}), (\d{4})", t) or re.fullmatch(r"(\d{1,2}) ([A-Za-z]+)\.? (\d{4})", t)
    if m:
        a, b, y = m.groups()
        mon, day = (a, b) if a[0].isalpha() else (b, a)
        return f"{y}-{_MONTHS[mon[:3].lower()]:02d}-{int(day):02d}"
    raise ValueError(t)
SRC = r"([A-Za-z]+-[A-Za-z]+)"
STATEMENT_RES = [
    re.compile(rf"^\[{SRC}, as of {DATE}\] (.+)\.$"),
    re.compile(rf"^{SRC} reports \(as of {DATE}\): (.+)\.$"),
    re.compile(rf"^As of {DATE}, according to {SRC}, (.+)\.$"),
]
ALIAS_RES = [
    re.compile(rf"^\[{SRC}\] Note: (.+) is another name used for (.+)\.$"),
    re.compile(rf"^{SRC} notes that (.+) is also referred to as (.+)\.$"),
]
AUDIT_RES = [
    re.compile(rf"^\[Audit-Desk\] Verified correction: the claim by {SRC} that .+ is false\.$"),
    re.compile(rf"^Audit-Desk has verified that {SRC}'s report that .+ was incorrect\.$"),
]


@lru_cache(maxsize=1)
def _tok():
    try:
        from transformers import AutoTokenizer
        return AutoTokenizer.from_pretrained(TOKENIZER)
    except Exception:  # offline fallback, approximate
        return None


def truncate(text: str, budget: int = BUDGET_TOKENS, keep: str = "head") -> str:
    tok = _tok()
    if tok is None:
        words = text.split(" ")
        n = int(budget / 1.4)
        return " ".join(words[:n] if keep == "head" else words[-n:])
    ids = tok(text, add_special_tokens=False)["input_ids"]
    if len(ids) <= budget:
        return text
    return tok.decode(ids[:budget] if keep == "head" else ids[-budget:])


def n_tokens(text: str) -> int:
    tok = _tok()
    return len(tok(text, add_special_tokens=False)["input_ids"]) if tok else int(len(text.split()) * 1.4)


class Grammar:
    """Splits a fact sentence into (subject, prompt, value) using public relation prompts."""

    def __init__(self, prompts):
        pats = []
        for p in sorted(set(prompts), key=len, reverse=True):
            pre, post = p.split("{}")
            pats.append((p, re.compile("^" + re.escape(pre) + r"(.+?)" + re.escape(post.rstrip()) + r" (.+)$")))
        self.pats = pats

    def parse(self, fact: str):
        for p, rx in self.pats:
            m = rx.match(fact)
            if m:
                return m.group(1), p, m.group(2)
        return None


def parse_stream(ep, grammar: Grammar):
    claims, aliases, flagged = [], {}, set()
    for sess_i, sess in enumerate(ep["sessions"]):
        for line in sess:
            if line.startswith("Audit-Desk") or line.startswith("[Audit-Desk]"):
                for rx in AUDIT_RES:
                    m = rx.match(line)
                    if m:
                        flagged.add(m.group(1))
                continue
            done = False
            for i, rx in enumerate(ALIAS_RES):
                m = rx.match(line)
                if m:
                    alias, subj = (m.group(2), m.group(3)) if i == 0 else (m.group(3), m.group(2))
                    aliases[alias] = subj
                    done = True
            if done:
                continue
            for i, rx in enumerate(STATEMENT_RES):
                m = rx.match(line)
                if not m:
                    continue
                if i == 2:
                    date, src, fact = m.group(1), m.group(2), m.group(3)
                else:
                    src, date, fact = m.group(1), m.group(2), m.group(3)
                parsed = grammar.parse(fact)
                if parsed:
                    claims.append({"subject": parsed[0], "prompt": parsed[1], "value": parsed[2],
                                   "date": norm_date(date), "source": src, "session": sess_i})
                break
    return claims, aliases, flagged


def render(facts) -> str:
    return "\n".join(f[0].replace("{}", f[1]).rstrip() + " " + f[2] + "." for f in facts)


def resolve(claims, aliases, exclude=()):
    best = {}
    for c in claims:
        if c["source"] in exclude:
            continue
        key = (aliases.get(c["subject"], c["subject"]), c["prompt"])
        if key not in best or c["date"] > best[key]["date"]:
            best[key] = c
    return [(p, s, c["value"]) for (s, p), c in best.items()]


def arm_memory(arm: str, ep, grammar: Grammar) -> str:
    if arm == "no_memory":
        return ""
    if arm == "oracle":
        return truncate(render([(t["prompt"], t["subject"], t["value"]) for t in ep["hidden"]["truth"].values()]))
    if arm == "write_all":
        return truncate("\n".join(l for s in ep["sessions"] for l in s), keep="tail")
    claims, aliases, flagged = parse_stream(ep, grammar)
    if arm == "newest_wins":
        return truncate(render(resolve(claims, aliases)))
    if arm == "symbolic":
        return truncate(render(resolve(claims, aliases, exclude=flagged)))
    raise ValueError(arm)


RULE_ARMS = ["oracle", "no_memory", "write_all", "newest_wins", "symbolic"]
