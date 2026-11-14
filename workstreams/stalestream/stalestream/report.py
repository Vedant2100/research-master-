"""Recompute aggregate metrics from raw eval files (CPU only, read-only).

Per arm (one eval_*.jsonl per seed): per-seed and seed-mean EM, per-tag EM, memory length and
fraction at the token budget, a reader-independent fact check, and paired bootstraps of the
seed-mean per-episode EM against a reference arm.

Fact check (does not use the reader): for each asked slot, a memory line that mentions the
subject (canonical name or any stream alias) is looked for. correct = such a line contains the
gold current value (or a value alias); stale = it instead holds another value the stream gave for
that subject (superseded or from the unreliable source); other = subject present, neither; missing =
no line mentions the subject. This separates "memory holds the right fact" from "reader got it".

  python -m stalestream.report --episodes $D/test.jsonl --aliases $D/value_aliases.json \
      --arm hdr=$R1/eval_s0_test.jsonl,$R1/eval_s1_test.jsonl --arm ctx=... --ref hdr
"""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics as st
from pathlib import Path

TAGS = ["plain", "alias", "out_of_order", "unreliable", "relative_date", "xref_date"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", s.lower())).strip()


def contains(line: str, phrase: str) -> bool:
    p = norm(phrase)
    return bool(p) and re.search(r"(?<!\w)" + re.escape(p) + r"(?!\w)", line) is not None


def fact_check(ep, memory, val_aliases):
    h = ep["hidden"]
    names = {}
    for a, canon in h["aliases"].items():
        names.setdefault(canon, [canon]).append(a)
    lines = [norm(l) for l in memory.splitlines() if l.strip()]
    out = []
    for slot, gold in zip(h["asked_slots"], h["answers"]):
        subj = h["truth"][slot]["subject"]
        golds = [gold] + val_aliases.get(gold, [])
        subj_names = names.get(subj, [subj])
        subj_lines = [l for l in lines if any(contains(l, n) for n in subj_names)]
        others = {k[3] for sess in h["must_keep"] for k in sess
                  if len(k) == 4 and k[2] in subj_names and k[3] not in golds}
        if not subj_lines:
            out.append("missing")
        elif any(contains(l, g) for l in subj_lines for g in golds):
            out.append("correct")
        elif any(contains(l, v) for l in subj_lines for v in others):
            out.append("stale")
        else:
            out.append("other")
    return out


def tags_of(ep, slot):
    return ep["hidden"]["difficulty"].get(slot) or ["plain"]


def bootstrap(diffs, n=10000, seed=0):
    rng = random.Random(seed)
    k = len(diffs)
    means = sorted(sum(diffs[rng.randrange(k)] for _ in range(k)) / k for _ in range(n))
    return sum(diffs) / k, means[int(0.025 * n)], means[int(0.975 * n)]


def load_arm(paths, eps):
    seeds = []
    for p in paths:
        p, _, arm = p.partition("@")
        rows = {r["episode_id"]: r for r in map(json.loads, open(p)) if not arm or r["arm"] == arm}
        missing = set(eps) - set(rows)
        assert not missing, f"{p}: {len(missing)} episodes missing"
        seeds.append(rows)
    return seeds


def summarize(name, seeds, eps, val_aliases, budget):
    ids = list(eps)
    em = [st.mean(s[i]["qa_exact_match"] for i in ids) for s in seeds]
    tag_hits = {t: [] for t in TAGS}
    facts = {"correct": 0, "stale": 0, "other": 0, "missing": 0}
    tag_fact = {t: [] for t in TAGS}
    toks = []
    for s in seeds:
        for i in ids:
            r, ep = s[i], eps[i]
            fc = fact_check(ep, r["memory"], val_aliases)
            toks.append(r["memory_tokens"])
            for slot, hit, f in zip(ep["hidden"]["asked_slots"], r["hits"], fc):
                facts[f] += 1
                for t in tags_of(ep, slot):
                    tag_hits[t].append(hit)
                    tag_fact[t].append(f == "correct")
    nf = sum(facts.values())
    return {"arm": name, "seeds": len(seeds), "em_per_seed": [round(x, 4) for x in em],
            "em_mean": round(st.mean(em), 4), "em_sd": round(st.stdev(em), 4) if len(em) > 1 else None,
            "em_by_tag": {t: round(st.mean(v), 4) for t, v in tag_hits.items() if v},
            "fact": {k: round(v / nf, 4) for k, v in facts.items()},
            "fact_correct_by_tag": {t: round(st.mean(v), 4) for t, v in tag_fact.items() if v},
            "memory_tokens_mean": round(st.mean(toks), 1),
            "frac_at_budget": round(sum(t >= budget for t in toks) / len(toks), 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--aliases", type=Path, required=True)
    ap.add_argument("--arm", action="append", required=True, help="name=path1[@arm],path2[@arm],... (one file per seed; @arm filters multi-arm files)")
    ap.add_argument("--ref", help="arm name for paired bootstraps")
    ap.add_argument("--budget", type=int, default=160)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    eps = {e["episode_id"]: e for e in map(json.loads, args.episodes.open())}
    val_aliases = json.loads(args.aliases.read_text())
    arms = {}
    for spec in args.arm:
        name, paths = spec.split("=", 1)
        arms[name] = load_arm(paths.split(","), eps)
    report = [summarize(n, s, eps, val_aliases, args.budget) for n, s in arms.items()]
    if args.ref:
        ids = list(eps)
        ref = [st.mean(s[i]["qa_exact_match"] for s in arms[args.ref]) for i in ids]
        for rep in report:
            if rep["arm"] == args.ref:
                continue
            seeds = arms[rep["arm"]]
            mean_ep = [st.mean(s[i]["qa_exact_match"] for s in seeds) for i in ids]
            d, lo, hi = bootstrap([a - b for a, b in zip(mean_ep, ref)])
            rep[f"vs_{args.ref}"] = {"seed_mean": [round(d, 4), round(lo, 4), round(hi, 4)],
                                    "per_seed": [[round(x, 4) for x in bootstrap([s[i]["qa_exact_match"] - r for i, r in zip(ids, ref)])]
                                                 for s in seeds]}
    for rep in report:
        print(json.dumps(rep))
    if args.out:
        args.out.write_text("".join(json.dumps(r) + "\n" for r in report))


if __name__ == "__main__":
    main()
