"""Privileged hints for on-policy self-distillation (OPSD) and date resolution for label checks.

Teacher hints are restricted to information DERIVABLE from the stream seen so far (current
and earlier sessions), computed for the teacher, never the answers:
  * resolved absolute dates for every statement of the current session (relative and
    cross-referenced dates resolved; derivable from the session's own text);
  * aliases introduced so far;
  * the unreliable source, ONLY once its audit line has appeared in or before the current session.
Answer values, oracle memory and future information are never included, to limit the
"privilege illusion" (the student imitating knowledge it cannot derive).
"""
from __future__ import annotations

import datetime as dt
import re

from .baselines import norm_date

XREF = re.compile(r"(?:(\d+) days (after|before)|the same day as) (\S+)'s report on (.+)")


def resolve_expr(expr: str, hdr: dt.date | None, prior: dict) -> dt.date | None:
    """Absolute date of a date expression; `prior` maps (source, surface name) -> date of
    earlier statements in the same session."""
    if expr == "earlier today":
        return hdr
    m = re.fullmatch(r"(\d+) days ago", expr)
    if m and hdr:
        return hdr - dt.timedelta(days=int(m.group(1)))
    m = re.fullmatch(r"(\d+) weeks ago", expr)
    if m and hdr:
        return hdr - dt.timedelta(days=7 * int(m.group(1)))
    m = XREF.fullmatch(expr)
    if m:
        base = prior.get((m.group(3), m.group(4)))
        if base is None:
            return None
        sign = -1 if m.group(2) == "before" else 1
        return base + dt.timedelta(days=sign * int(m.group(1) or 0))
    try:
        return dt.date.fromisoformat(norm_date(expr))
    except (ValueError, KeyError):
        return None


def session_dates(ep, s: int):
    """Per-line absolute date for session s (None for non-statement lines)."""
    sess, keeps = ep["sessions"][s], ep["hidden"]["must_keep"][s]
    hdr = None
    if sess and sess[0].startswith("Session date:"):
        hdr = dt.date.fromisoformat(norm_date(sess[0].split("Session date: ", 1)[1]))
    prior, out = {}, []
    for keep in keeps:
        if len(keep) == 4 and "Audit-Desk" not in keep:
            src, expr, name, _ = keep
            d = resolve_expr(expr, hdr, prior)
            prior[(src, name)] = d
            out.append(d)
        else:
            out.append(None)
    return out


def teacher_statements(ep, s: int):
    """The session's statements, each statement annotated with its resolved absolute date."""
    dates = session_dates(ep, s)
    return [f"{line} [resolved date: {d.isoformat()}]" if d else line
            for line, d in zip(ep["sessions"][s], dates)]


def teacher_notes(ep, s: int) -> str:
    """Episode-level hints derivable from sessions 0..s."""
    h = ep["hidden"]
    seen = "\n".join(l for sess in ep["sessions"][: s + 1] for l in sess)
    aliases = [f"{a} = {n}" for a, n in h["aliases"].items() if a in seen]
    audited = "Audit-Desk" in seen and h["unreliable_source"] in seen and any(
        "Audit-Desk" in l and h["unreliable_source"] in l for l in seen.splitlines())
    notes = []
    if aliases:
        notes.append("Aliases introduced so far: " + "; ".join(aliases) + ".")
    if audited:
        notes.append(f"{h['unreliable_source']} has been caught making a false claim: treat all of its claims as unreliable.")
    return "\n".join(notes)
