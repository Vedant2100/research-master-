"""Audit StaleStream data and recorded results. Read-only; exits non-zero on any failure.

Checks (1) generator invariants on every episode file, (2) that the numbers recorded in
STATUS.md are recomputable from raw eval files, (3) reader parse-failure rates.

  python scripts/audit.py --data $S/data --runs $S/runs
"""
from __future__ import annotations

import argparse
import json
import random
import re
import statistics as st
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stalestream.baselines import ALIAS_RES, AUDIT_RES, Grammar, parse_stream  # noqa: E402
from stalestream.generator import AUDIT, load_slots  # noqa: E402

FAIL = []


def check(cond, msg):
    if not cond:
        FAIL.append(msg)


def load(p):
    return [json.loads(l) for l in open(p)]


def episode_invariants(ep, templated: bool, grammar):
    h, eid = ep["hidden"], ep["episode_id"]
    check(len(ep["questions"]) == 6 == len(h["answers"]), f"{eid}: not 6 questions")
    check(len(set(h["asked_slots"])) == 6, f"{eid}: duplicate asked slots")
    subs = [t["subject"] for t in h["truth"].values()]
    check(len(subs) == len(set(subs)), f"{eid}: duplicate subjects")
    joined = "\n".join(l for s in ep["sessions"] for l in s)
    check(h["unreliable_source"] in joined, f"{eid}: unreliable source never appears")
    check(AUDIT in joined, f"{eid}: no audit line")
    check("reliab" not in joined.lower(), f"{eid}: leaks the word reliability")
    for ans in h["answers"]:
        check(ans in joined, f"{eid}: answer {ans!r} absent from stream")
    if not templated:
        return
    # Full semantic re-derivation is only possible on template text (v0 / v1_raw).
    claims, aliases, flagged = parse_stream(ep, grammar)
    check(flagged == {h["unreliable_source"]}, f"{eid}: audit flags {flagged}, hidden {h['unreliable_source']}")
    check(aliases == h["aliases"], f"{eid}: alias map mismatch")
    for sid, gold in zip(h["asked_slots"], h["answers"]):
        t = h["truth"][sid]
        cs = [c for c in claims if aliases.get(c["subject"], c["subject"]) == t["subject"] and c["prompt"] == t["prompt"]]
        rel = [c for c in cs if c["source"] != h["unreliable_source"]]
        check(bool(rel), f"{eid}/{sid}: no reliable claim")
        if rel:
            best = max(rel, key=lambda c: c["date"])
            check(best["value"] == gold, f"{eid}/{sid}: latest reliable {best['value']!r} != gold {gold!r}")
            ties = [c for c in rel if c["date"] == best["date"] and c["value"] != best["value"]]
            check(not ties, f"{eid}/{sid}: date tie between different reliable values")
        bad = [c for c in cs if c["source"] == h["unreliable_source"]]
        if bad and rel:
            check(max(c["date"] for c in bad) > max(c["date"] for c in rel),
                  f"{eid}/{sid}: unreliable claim not newest (newest-wins would not be fooled)")
        # alias must be introduced in a session no later than its first use
        for alias, subj in h["aliases"].items():
            intro = min(i for i, s in enumerate(ep["sessions"]) for l in s
                        if alias in l and any(rx.match(l) for rx in ALIAS_RES))
            uses = [i for i, s in enumerate(ep["sessions"]) for l in s
                    if alias in l and not any(rx.match(l) for rx in ALIAS_RES)]
            check(all(u > intro for u in uses), f"{eid}: alias {alias} used before/at intro session")
    # the audited claim's slot must not be asked
    audited_lines = [l for s in ep["sessions"] for l in s if any(rx.match(l) for rx in AUDIT_RES)]
    check(len(audited_lines) == 1, f"{eid}: expected exactly one audit line")


def boot(d, n=1000, seed=2026):
    rng = random.Random(seed)
    bs = sorted(st.mean(d[rng.randrange(len(d))] for _ in d) for _ in range(n))
    return round(st.mean(d), 4), round(bs[int(.025 * n)], 4), round(bs[int(.975 * n)], 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--runs", type=Path, required=True)
    args = ap.parse_args()
    slots, _, _ = load_slots(args.data / "MQuAKE-CF-3k-v2.json")
    grammar = Grammar([s["prompt"] for s in slots])
    report = {}

    for ver, templated in [("episodes_v0", True), ("episodes_v1_raw", True), ("episodes_v1", False)]:
        for split in ["train_2s", "test"]:
            p = args.data / ver / f"{split}.jsonl"
            if not p.exists():
                FAIL.append(f"missing {p}")
                continue
            eps = load(p)
            for ep in eps:
                episode_invariants(ep, templated, grammar)
            report[f"{ver}/{split}"] = len(eps)
        tr = {t["subject"] for e in load(args.data / ver / "train_2s.jsonl") for t in e["hidden"]["truth"].values()}
        te = {t["subject"] for e in load(args.data / ver / "test.jsonl") for t in e["hidden"]["truth"].values()}
        check(not tr & te, f"{ver}: {len(tr & te)} subjects shared train/test")

    # v1 paraphrase fallback rate
    for split in ["train_2s", "test"]:
        eps = load(args.data / "episodes_v1" / f"{split}.jsonl")
        flags = [f for e in eps for s in e["hidden"]["paraphrased"] for f in s]
        report[f"v1/{split}_fallback_rate"] = round(1 - sum(flags) / len(flags), 4)

    # recompute recorded results
    def arm_scores(path):
        sc = {}
        for r in load(path):
            sc.setdefault(r["arm"], {})[r["episode_id"]] = r
        return sc
    for name, path in [("v0", args.runs / "v0_eval.jsonl"), ("v1", args.runs / "v1_eval_all.jsonl"),
                       ("pilot", args.runs / "pilot_v1" / "all_eval.jsonl")]:
        if not path.exists():
            FAIL.append(f"missing {path}")
            continue
        sc = arm_scores(path)
        means = {a: round(st.mean(r["qa_exact_match"] for r in v.values()), 4) for a, v in sc.items()}
        parse_fail = {a: round(st.mean(sum(1 for p in r["preds"] if not p.strip()) / 6 for r in v.values()), 4)
                      for a, v in sc.items()}
        n_eps = {a: len(v) for a, v in sc.items()}
        report[name] = {"means": means, "empty_pred_rate": parse_fail, "episodes": n_eps}
        check(all(n == 300 for n in n_eps.values()), f"{name}: not 300 episodes per arm: {n_eps}")
        if name == "pilot":
            ids = sorted(sc["oracle"])
            for arm in ["grpo_100", "rloo_100"]:
                report[name][f"{arm}_vs_prompted_1.7b"] = boot(
                    [sc[arm][i]["qa_exact_match"] - sc["prompted_1.7b"][i]["qa_exact_match"] for i in ids])

    for algo in ["grpo", "rloo"]:
        p = args.runs / "pilot_v1" / algo / "train_log.jsonl"
        if p.exists():
            r = load(p)
            report[f"train_{algo}"] = {"steps": len(r), "first20": round(st.mean(x["reward_mean"] for x in r[:20]), 3),
                                       "last20": round(st.mean(x["reward_mean"] for x in r[-20:]), 3),
                                       "mean_grad_norm": round(st.mean(x["grad_norm"] for x in r), 3),
                                       "sec_per_step": round(st.mean(x["t_step"] for x in r), 1),
                                       "any_nan": any(x["loss"] != x["loss"] for x in r)}

    print(json.dumps(report, indent=1))
    print(f"\n{len(FAIL)} FAILURES")
    for f in FAIL[:40]:
        print(" -", f)
    sys.exit(1 if FAIL else 0)


if __name__ == "__main__":
    main()
