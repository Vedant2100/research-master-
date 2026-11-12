"""Re-derive v3 labels from the stream text: resolve absolute / session-relative /
cross-referenced dates, then latest reliable claim per asked slot must equal the gold answer.
Also counts ambiguous cross-references ((source, subject) reported twice in a session)."""
import datetime as dt
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from stalestream.baselines import norm_date  # noqa: E402
from stalestream.generator import fact_text  # noqa: E402

XREF = re.compile(r"(?:(\d+) days (after|before)|the same day as) (\S+)'s report on (.+)")


def resolve(expr, hdr, prior):
    if expr == "earlier today":
        return hdr
    m = re.fullmatch(r"(\d+) days ago", expr)
    if m:
        return hdr - dt.timedelta(days=int(m.group(1)))
    m = re.fullmatch(r"(\d+) weeks ago", expr)
    if m:
        return hdr - dt.timedelta(days=7 * int(m.group(1)))
    m = XREF.fullmatch(expr)
    if m:
        sign = -1 if m.group(2) == "before" else 1
        return prior[(m.group(3), m.group(4))] + dt.timedelta(days=sign * int(m.group(1) or 0))
    return dt.date.fromisoformat(norm_date(expr))


def check(path):
    bad = amb = n = 0
    for l in open(path):
        ep = json.loads(l)
        h = ep["hidden"]
        prompts = [t["prompt"] for t in h["truth"].values()]
        claims = []
        for sess, mk in zip(ep["sessions"], h["must_keep"]):
            hdr = dt.date.fromisoformat(norm_date(sess[0].split("Session date: ")[1]))
            cnt = Counter((k[0], k[2]) for k in mk if len(k) == 4 and "Audit-Desk" not in k)
            prior = {}
            for line, keep in zip(sess, mk):
                if len(keep) != 4 or "Audit-Desk" in keep:
                    continue
                src, expr, name, val = keep
                m = XREF.fullmatch(expr)
                if m and cnt[(m.group(3), m.group(4))] > 1:
                    amb += 1
                d = resolve(expr, hdr, prior)
                prior[(src, name)] = d
                p = next((p for p in prompts if fact_text(p, name, val) in line), None)
                if p:
                    claims.append((h["aliases"].get(name, name), p, val, d, src))
        for sid, gold in zip(h["asked_slots"], h["answers"]):
            t = h["truth"][sid]
            rel = [c for c in claims if c[0] == t["subject"] and c[1] == t["prompt"] and c[4] != h["unreliable_source"]]
            n += 1
            bad += not rel or max(rel, key=lambda c: c[3])[2] != gold
    return n, bad, amb


if __name__ == "__main__":
    for p in sys.argv[1:]:
        n, bad, amb = check(p)
        print(f"{p}: asked slots {n}, label mismatches {bad}, ambiguous xref lines {amb}")
