"""Line-level extraction diagnostics from `extract.py --dump` files (CPU, read-only).

Date accuracy is scored against gold dates resolved from the stream (`dates.gold_dates`), separately
for absolute, relative-to-session and cross-referenced dates. Lines: non-audit statements only.

  python -m stalestream.diag --episodes test.jsonl --mquake MQ.json --dump name=dump.jsonl [...]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict
from pathlib import Path

from .baselines import norm_date
from .dates import gold_dates
from .extract import grammar, parse_json


def _d(x):
    try:
        return dt.date.fromisoformat(norm_date(str(x)))
    except (ValueError, KeyError):
        return None


def winner_check(ep, ext_dates):
    """Per asked slot: with every field at gold except the extracted dates, does the latest claim among
    non-audited sources give the gold answer? Isolates conflict-resolution errors caused by dates.
    Unparseable extracted dates count as earliest. Returns {tag: [ok, n]} including 'all'."""
    h = ep["hidden"]
    flagged = {k[1] for sess in h["must_keep"] for k in sess if len(k) == 4 and k[0] == "Audit-Desk"}
    claims = defaultdict(list)
    for (s, l) in ep["_gd"]:
        src, _, name, val = h["must_keep"][s][l]
        if src not in flagged:
            claims[h["aliases"].get(name, name)].append((ext_dates.get((s, l)) or dt.date.min, val))
    out = defaultdict(lambda: [0, 0])
    for slot, ans in zip(h["asked_slots"], h["answers"]):
        cl = claims[h["truth"][slot]["subject"]]
        top = max(d for d, _ in cl)
        ok = {v for d, v in cl if d == top} == {ans}
        for t in ["all"] + (h["difficulty"].get(slot) or ["plain"]):
            out[t][0] += ok
            out[t][1] += 1
    return out


def diag(eps, rows, label_to_rel):
    acc = defaultdict(lambda: [0, 0])
    ext = defaultdict(dict)
    for r in rows:
        ep = eps[r["episode_id"]]
        s, l = r["line"]
        g = ep["_gd"].get((s, l))
        if g is None:
            continue
        src, _, name, val = ep["hidden"]["must_keep"][s][l]
        gold, kind = g
        it = parse_json(r["raw"])
        fact = isinstance(it, dict) and it.get("type") == "fact"
        d = _d(it.get("date")) if fact else None
        ext[r["episode_id"]][(s, l)] = d
        err = abs((d - dt.date.fromisoformat(gold)).days) if d else None
        checks = {"is_fact": fact, "date_ok": err == 0, "date_30d": err is not None and err <= 30,
                  "value_ok": fact and str(it.get("value", "")).strip() == val,
                  "subject_ok": fact and str(it.get("subject", "")).strip() == name,
                  "source_ok": fact and str(it.get("source", "")).strip() == src,
                  "relation_valid": fact and str(it.get("relation", "")).strip() in label_to_rel}
        for k, v in checks.items():
            for grp in ("all", kind):
                acc[(grp, k)][0] += bool(v)
                acc[(grp, k)][1] += 1
    win = defaultdict(lambda: [0, 0])
    for eid, ext_dates in ext.items():
        for t, (a, b) in winner_check(eps[eid], ext_dates).items():
            win[t][0] += a
            win[t][1] += b
    return {f"{g}.{k}": round(a / b, 4) for (g, k), (a, b) in sorted(acc.items())} | \
        {f"n.{g}": b for (g, k), (a, b) in acc.items() if k == "date_ok"} | \
        {f"winner_ok.{t}": round(a / b, 4) for t, (a, b) in sorted(win.items())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=Path, required=True)
    ap.add_argument("--mquake", type=Path, required=True)
    ap.add_argument("--dump", action="append", required=True, help="name=path")
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    _, label_to_rel, _ = grammar(args.mquake)
    eps = {e["episode_id"]: e for e in map(json.loads, args.episodes.open())}
    for ep in eps.values():
        ep["_gd"] = gold_dates(ep)
    res = []
    for spec in args.dump:
        name, path = spec.split("=", 1)
        res.append({"arm": name, **diag(eps, list(map(json.loads, open(path))), label_to_rel)})
        print(json.dumps(res[-1]))
    if args.out:
        args.out.write_text("".join(json.dumps(r) + "\n" for r in res))


if __name__ == "__main__":
    main()
