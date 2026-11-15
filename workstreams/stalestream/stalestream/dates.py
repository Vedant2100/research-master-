"""Gold absolute dates for every v3 statement line, resolved from the stream itself (diagnostic only).

v3 statement dates are absolute, relative to the session header ("40 days ago", "3 weeks ago",
"earlier today"), or cross-referenced to one earlier statement in the same session ("441 days before
Source-B's report on Chris Rock"; the generator guarantees the anchor is unique and not itself a
cross-reference). The old `fact_date_ok` compared extractions to the raw expression, which only
parses for absolute dates, so every relative/cross-referenced line counted as wrong (ceiling ~0.68).

  gold_dates(ep) -> {(session, line): (iso_date, kind)}   kind in absolute_date|relative_date|xref_date
"""
from __future__ import annotations

import datetime as dt
import re

from .baselines import norm_date

AUDIT = "Audit-Desk"
_REL = re.compile(r"(\d+) (days|weeks) ago")
_XREF = re.compile(r"(?:the same day as|(\d+) days (after|before)) (.+?)'s report on (.+)")


def _header_date(sess):
    for line in sess:
        if line.startswith("Session date:"):
            return dt.date.fromisoformat(norm_date(line.split(":", 1)[1]))
    raise ValueError("no session header")


def gold_dates(ep):
    out = {}
    for s, (sess, keep) in enumerate(zip(ep["sessions"], ep["hidden"]["must_keep"])):
        hdr = _header_date(sess)
        stmts = {l: k for l, k in enumerate(keep) if len(k) == 4 and k[0] != AUDIT}
        direct = {}
        for l, (src, expr, name, val) in stmts.items():
            if _XREF.fullmatch(expr):
                continue
            if expr == "earlier today":
                direct[l] = (hdr, "relative_date")
            elif m := _REL.fullmatch(expr):
                n = int(m.group(1)) * (7 if m.group(2) == "weeks" else 1)
                direct[l] = (hdr - dt.timedelta(days=n), "relative_date")
            else:
                direct[l] = (dt.date.fromisoformat(norm_date(expr)), "absolute_date")
        for l, (src, expr, name, val) in stmts.items():
            m = _XREF.fullmatch(expr)
            if not m:
                continue
            delta = 0 if m.group(1) is None else int(m.group(1)) * (1 if m.group(2) == "after" else -1)
            anchors = [a for a in direct if stmts[a][0] == m.group(3) and stmts[a][2] == m.group(4)]
            assert len(anchors) == 1, (ep["episode_id"], s, l, expr, anchors)
            out[(s, l)] = ((direct[anchors[0]][0] + dt.timedelta(days=delta)).isoformat(), "xref_date")
        for l, (d, kind) in direct.items():
            out[(s, l)] = (d.isoformat(), kind)
    return out


def check(ep):
    """Truth must be recomputable with gold dates: latest-dated claim from a non-audited source."""
    h = ep["hidden"]
    gd = gold_dates(ep)
    canon = h["aliases"]
    flagged = {k[1] for sess in h["must_keep"] for k in sess if len(k) == 4 and k[0] == AUDIT}
    best = {}
    for (s, l), (d, _) in gd.items():
        src, _, name, val = h["must_keep"][s][l]
        if src in flagged:
            continue
        subj = canon.get(name, name)
        if subj not in best or d > best[subj][0]:
            best[subj] = (d, val)
    for slot, ans in zip(h["asked_slots"], h["answers"]):
        subj = h["truth"][slot]["subject"]
        assert best[subj][1] == ans, (ep["episode_id"], slot, best[subj], ans)
