"""StaleStream episode generator (v0).

Builds multi-session episodes of dated, sourced natural-language statements from
MQuAKE counterfactual edits. Ground truth is recomputed from event dates and the
hidden source reliability, never from delivery order.

Per episode:
  * 6-10 slots (subject, relation) from MQuAKE requested rewrites, distinct subjects.
  * True timeline per slot: target_true (old) -> target_new (new), and in 25% of slots a
    third value from the same relation's pool. Current = latest-dated reliable value.
  * Out-of-order delivery: each statement lands in a uniformly random session.
  * Aliasing: half the subjects get an alias introduced in an early session; statements
    in later sessions use the alias 70% of the time.
  * Unreliable source: one of 4 sources (hidden, per episode) makes newer-dated false
    claims on ~40% of slots. One of its claims, on a slot that is NOT asked, is flagged
    by an Audit-Desk correction: in-stream evidence that the source is unreliable.
  * Six questions ask current values, preferring hard slots.

Everything under "hidden" is privileged and must never reach a non-privileged writer.

  python -m stalestream.generator --mquake MQuAKE-CF-3k-v2.json --out DIR
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

SOURCES = ["Source-A", "Source-B", "Source-C", "Source-D"]
AUDIT = "Audit-Desk"

STATEMENT_TEMPLATES = [
    "[{source}, as of {date}] {fact}.",
    "{source} reports (as of {date}): {fact}.",
    "As of {date}, according to {source}, {fact}.",
]
ALIAS_TEMPLATES = [
    "[{source}] Note: {alias} is another name used for {subject}.",
    "{source} notes that {subject} is also referred to as {alias}.",
]
AUDIT_TEMPLATES = [
    "[{audit}] Verified correction: the claim by {bad} that {fact} is false.",
    "{audit} has verified that {bad}'s report that {fact} was incorrect.",
]


def fact_text(prompt: str, subject: str, value: str) -> str:
    return prompt.replace("{}", subject).rstrip() + " " + value


def _date(rng: random.Random, lo: dt.date, hi: dt.date) -> dt.date:
    return lo + dt.timedelta(days=rng.randrange(max(1, (hi - lo).days + 1)))


def load_slots(path: Path):
    """Return (slots, value_pool_by_relation, value_aliases)."""
    data = json.loads(Path(path).read_text())
    slots, pool, aliases, seen = [], defaultdict(set), defaultdict(set), set()
    for case in data:
        hop_alias = defaultdict(set)
        for hop in case.get("single_hops", []) + case.get("new_single_hops", []):
            hop_alias[hop["answer"]].update(hop.get("answer_alias", []))
        for rw in case["requested_rewrite"]:
            key = (rw["subject"], rw["relation_id"])
            old, new = rw["target_true"]["str"], rw["target_new"]["str"]
            if key in seen or old == new or "{}" not in rw["prompt"]:
                continue
            seen.add(key)
            slots.append({"subject": rw["subject"], "relation": rw["relation_id"],
                          "prompt": rw["prompt"], "question": rw["question"], "old": old, "new": new})
            pool[rw["relation_id"]].update([old, new])
            for v in (old, new):
                aliases[v].update(hop_alias.get(v, ()))
    return slots, {k: sorted(v) for k, v in pool.items()}, {k: sorted(v) for k, v in aliases.items()}


def _bucket(subject: str) -> float:
    return int(hashlib.sha256(subject.encode()).hexdigest(), 16) % 1000 / 1000


def split_subjects(slots, test_frac=0.15):
    """Entity-disjoint 2-way split by a stable hash of the subject string (v0/v1)."""
    train = [s for s in slots if _bucket(s["subject"]) >= test_frac]
    test = [s for s in slots if _bucket(s["subject"]) < test_frac]
    assert not {s["subject"] for s in train} & {s["subject"] for s in test}
    return train, test


def split_subjects3(slots, test_frac=0.15, val_frac=0.15, exclude=frozenset()):
    """3-way split (v2+): test buckets are identical to the 2-way split; val is carved out of
    the old train range. Subjects in `exclude` (e.g. FactConsolidation entities) are dropped."""
    keep = [s for s in slots if s["subject"] not in exclude]
    test = [s for s in keep if _bucket(s["subject"]) < test_frac]
    val = [s for s in keep if test_frac <= _bucket(s["subject"]) < test_frac + val_frac]
    train = [s for s in keep if _bucket(s["subject"]) >= test_frac + val_frac]
    a, b, c = ({x["subject"] for x in g} for g in (train, val, test))
    assert not (a & b or a & c or b & c)
    return train, val, test


def make_alias(rng: random.Random, subject: str) -> str:
    initials = "".join(w[0] for w in subject.split() if w[:1].isalpha()).upper() or "X"
    return f"{initials}-{rng.randrange(10, 99)}"


MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]


def format_date(rng: random.Random, d: dt.date, style: str) -> str:
    """'iso' (v0) or 'mixed' (v1): one of several absolute surface forms."""
    if style == "iso":
        return d.isoformat()
    forms = [d.isoformat(), f"{MONTHS[d.month - 1]} {d.day}, {d.year}", f"{d.day} {MONTHS[d.month - 1]} {d.year}",
             f"{MONTHS[d.month - 1][:3]}. {d.day}, {d.year}", f"{d.year}/{d.month:02d}/{d.day:02d}"]
    return rng.choice(forms)


CONFLICT_TAGS = {"alias", "unreliable", "out_of_order"}


def build_episode(rng: random.Random, ep_id: str, slots, pool, n_sessions: int, date_style: str = "iso",
                  k_range=(6, 10), conflict_questions: bool = False, rng_order: str = "v0",
                  dates_v3: bool = False):
    """rng_order reproduces historical data: "v0" (and v2+) draws template before source/date;
    "v1" is the draw order that produced the existing v1 data (source/date before template)."""
    k = rng.randint(*k_range)
    chosen, subjects = [], set()
    for s in rng.sample(slots, min(len(slots), 200)):
        if s["subject"] not in subjects and len(pool[s["relation"]]) >= 3:
            chosen.append(s)
            subjects.add(s["subject"])
        if len(chosen) == k:
            break
    bad = rng.choice(SOURCES)
    good = [x for x in SOURCES if x != bad]

    events, truth, hard, alias_of = [], {}, {}, {}
    for i, s in enumerate(chosen):
        sid = f"s{i}"
        d1 = _date(rng, dt.date(2019, 1, 1), dt.date(2022, 6, 30))
        d2 = _date(rng, d1 + dt.timedelta(days=30), dt.date(2024, 6, 30))
        timeline = [(s["old"], d1), (s["new"], d2)]
        if rng.random() < 0.25:
            others = [v for v in pool[s["relation"]] if v not in (s["old"], s["new"])]
            timeline.append((rng.choice(others), _date(rng, d2 + dt.timedelta(days=30), dt.date(2025, 6, 30))))
        for value, d in timeline:
            events.append({"slot": sid, "value": value, "date": d, "source": rng.choice(good), "reliable": True})
        truth[sid] = timeline[-1][0]
        hard[sid] = set()
        if rng.random() < 0.5:
            alias_of[sid] = make_alias(rng, s["subject"])
            hard[sid].add("alias")

    sids = list(truth)
    lie = [x for x in sids if rng.random() < 0.4]
    if len(lie) < 2:
        lie = rng.sample(sids, 2)
    for sid in lie:
        s = chosen[int(sid[1:])]
        latest = max(e["date"] for e in events if e["slot"] == sid)
        wrong = rng.choice([v for v in pool[s["relation"]] if v != truth[sid]])
        events.append({"slot": sid, "value": wrong, "source": bad, "reliable": False,
                       "date": _date(rng, latest + dt.timedelta(days=1), latest + dt.timedelta(days=400))})
        hard[sid].add("unreliable")
    audited = rng.choice(lie)

    for e in events:
        e["session"] = rng.randrange(n_sessions)
    for sid in sids:
        evs = sorted((e for e in events if e["slot"] == sid and e["reliable"]), key=lambda e: e["date"])
        if any(a["session"] > b["session"] for a, b in zip(evs, evs[1:])):
            hard[sid].add("out_of_order")

    candidates = [x for x in sids if x != audited]
    if conflict_questions:  # v2: only ask about conflicted slots when there are enough of them
        conflicted = [x for x in candidates if hard[x] & CONFLICT_TAGS]
        rest = [x for x in candidates if not hard[x] & CONFLICT_TAGS]
        rng.shuffle(conflicted)
        rng.shuffle(rest)
        candidates = conflicted + rest
        asked = candidates[:6]
    else:
        asked = sorted(candidates, key=lambda x: (-len(hard[x]), rng.random()))[:6]
    if len(asked) < 6:  # only possible when k == 6
        asked.append(audited)

    # Each line is (sort key, text, must_keep strings). must_keep is privileged metadata
    # used only by the paraphraser to verify that the label-bearing strings survive.
    sessions = [[] for _ in range(n_sessions)]
    alias_intro = {x: rng.randrange(max(1, n_sessions - 1)) for x in alias_of}
    for sid, sess in alias_intro.items():
        if rng_order == "v1":
            src = rng.choice(good)
            tmpl = rng.choice(ALIAS_TEMPLATES)
        else:
            tmpl = rng.choice(ALIAS_TEMPLATES)
            src = rng.choice(good)
        subj = chosen[int(sid[1:])]["subject"]
        sessions[sess].append((-1.0, tmpl.format(source=src, alias=alias_of[sid], subject=subj),
                               [src, alias_of[sid], subj]))
    if dates_v3:
        _v3_statements(rng, events, chosen, alias_of, alias_intro, sessions, n_sessions, date_style, hard)
    for e in ([] if dates_v3 else events):
        s = chosen[int(e["slot"][1:])]
        name = s["subject"]
        if e["slot"] in alias_of and e["session"] > alias_intro[e["slot"]] and rng.random() < 0.7:
            name = alias_of[e["slot"]]
        if rng_order == "v1":
            date = format_date(rng, e["date"], date_style)
            tmpl = rng.choice(STATEMENT_TEMPLATES)
        else:
            tmpl = rng.choice(STATEMENT_TEMPLATES)
            date = format_date(rng, e["date"], date_style)
        text = tmpl.format(
            source=e["source"], date=date, fact=fact_text(s["prompt"], name, e["value"]))
        sessions[e["session"]].append((rng.random(), text, [e["source"], date, name, e["value"]]))
    claim = next(e for e in events if e["slot"] == audited and not e["reliable"])
    s = chosen[int(audited[1:])]
    sessions[rng.randrange(claim["session"], n_sessions)].append((rng.random(), rng.choice(AUDIT_TEMPLATES).format(
        audit=AUDIT, bad=bad, fact=fact_text(s["prompt"], s["subject"], claim["value"])),
        [AUDIT, bad, s["subject"], claim["value"]]))
    sessions = [sorted(sess, key=lambda x: (x[0], x[1])) for sess in sessions]
    must_keep = [[m for _, _, m in sess] for sess in sessions]
    sessions = [[t for _, t, _ in sess] for sess in sessions]

    return {
        "episode_id": ep_id,
        "sessions": sessions,
        "questions": [chosen[int(x[1:])]["question"] for x in asked],
        "hidden": {
            "answers": [truth[x] for x in asked],
            "asked_slots": asked,
            "truth": {x: {"subject": chosen[int(x[1:])]["subject"], "prompt": chosen[int(x[1:])]["prompt"],
                          "relation": chosen[int(x[1:])]["relation"], "value": truth[x]} for x in sids},
            "unreliable_source": bad,
            "aliases": {alias_of[x]: chosen[int(x[1:])]["subject"] for x in alias_of},
            "difficulty": {x: sorted(hard[x]) for x in asked},
            "must_keep": must_keep,
        },
    }


def _v3_statements(rng, events, chosen, alias_of, alias_intro, sessions, n_sessions, date_style, hard):
    """v3 dates. Each session opens with a dated header. Each statement's date is absolute (~40%),
    relative to the session date (~35%: "N days ago", "N weeks ago", "earlier today"), or relative
    to an EARLIER statement in the same session (~25%: "N days after Source-X's report on Y").
    Cross-references can only be resolved with the other line in view: per-line extraction loses them."""
    sdates, prev = [], None
    for k in range(n_sessions):
        mx = max([e["date"] for e in events if e["session"] <= k] or [dt.date(2019, 1, 1)])
        d = mx + dt.timedelta(days=rng.randint(1, 45))
        if prev is not None and d <= prev:
            d = prev + dt.timedelta(days=rng.randint(1, 10))
        sdates.append(d)
        prev = d
    for k, d in enumerate(sdates):
        hdr = f"Session date: {format_date(rng, d, date_style)}"
        sessions[k].append((-2.0, hdr, [hdr]))
    keyed = sorted(((rng.random(), e) for e in events), key=lambda x: (x[1]["session"], x[0]))
    # pass 1: surface names, templates and expression draws
    plan = []
    for key, e in keyed:
        s = chosen[int(e["slot"][1:])]
        name = s["subject"]
        if e["slot"] in alias_of and e["session"] > alias_intro[e["slot"]] and rng.random() < 0.7:
            name = alias_of[e["slot"]]
        plan.append((key, e, s, name, rng.choice(STATEMENT_TEMPLATES), rng.random()))
    # a cross-reference may only point at a (source, surface name) reported once in its session
    counts = Counter((e["session"], e["source"], name) for _, e, _, name, _, _ in plan)
    anchors = {k: [] for k in range(n_sessions)}
    for key, e, s, name, tmpl, u in plan:
        k = e["session"]
        cand = [a for a in anchors[k] if a[0]["slot"] != e["slot"] and counts[(k, a[0]["source"], a[1])] == 1]
        ago = (sdates[k] - e["date"]).days
        if u < 0.25 and cand:
            a, aname = rng.choice(cand)
            delta = (e["date"] - a["date"]).days
            ref = f"{a['source']}'s report on {aname}"
            expr = (f"the same day as {ref}" if delta == 0 else
                    f"{abs(delta)} days {'after' if delta > 0 else 'before'} {ref}")
            kind = "xref_date"
        elif u < 0.60 and 0 <= ago <= 400:
            expr = ("earlier today" if ago == 0 else
                    f"{ago // 7} weeks ago" if ago % 7 == 0 and ago <= 70 else f"{ago} days ago")
            kind = "relative_date"
        else:
            expr = format_date(rng, e["date"], date_style)
            kind = "absolute_date"
        text = tmpl.format(source=e["source"], date=expr, fact=fact_text(s["prompt"], name, e["value"]))
        sessions[k].append((key, text, [e["source"], expr, name, e["value"]]))
        e["date_kind"] = kind
        if kind != "xref_date":
            anchors[k].append((e, name))
        if kind != "absolute_date":
            hard[e["slot"]].add(kind)


def validate(ep):
    """Assert the labels are recomputable from the stream and nothing leaks."""
    h = ep["hidden"]
    assert len(ep["questions"]) == 6 == len(h["answers"]) == len(set(h["asked_slots"]))
    joined = "\n".join(t for s in ep["sessions"] for t in s)
    for sid, ans in zip(h["asked_slots"], h["answers"]):
        assert ans == h["truth"][sid]["value"]
        assert ans in joined, f"answer {ans!r} never stated in {ep['episode_id']}"
    assert "reliab" not in joined.lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mquake", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--n-train", type=int, default=2000)
    ap.add_argument("--n-test", type=int, default=300)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--date-style", choices=["iso", "mixed"], default="iso")
    ap.add_argument("--slots", type=int, nargs=2, default=[6, 10], metavar=("MIN", "MAX"))
    ap.add_argument("--conflict-questions", action="store_true")
    ap.add_argument("--split3", action="store_true", help="train/val/test (v2+)")
    ap.add_argument("--dates-v3", action="store_true", help="session headers + relative/cross-referenced dates")
    ap.add_argument("--rng-order", choices=["v0", "v1"], default="v0",
                    help="v1 reproduces the existing v1 data (seed 2027, --date-style mixed)")
    ap.add_argument("--n-val", type=int, default=300)
    ap.add_argument("--exclude-subjects", type=Path, default=None, help="JSON list of subjects to drop")
    args = ap.parse_args()
    slots, pool, aliases = load_slots(args.mquake)
    args.out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(args.seed)
    if args.split3:
        exclude = frozenset(json.loads(args.exclude_subjects.read_text())) if args.exclude_subjects else frozenset()
        train, val, test = split_subjects3(slots, exclude=exclude)
        plan = [("train_2s", train, args.n_train, (2, 2)), ("val", val, args.n_val, (3, 4)),
                ("test", test, args.n_test, (3, 4))]
    else:
        train, test = split_subjects(slots)
        val = []
        plan = [("train_2s", train, args.n_train, (2, 2)), ("test", test, args.n_test, (3, 4))]
    for name, src, n, (lo, hi) in plan:
        with (args.out / f"{name}.jsonl").open("w") as f:
            for i in range(n):
                ep = build_episode(rng, f"{name}-{i:05d}", src, pool, rng.randint(lo, hi), args.date_style,
                                   tuple(args.slots), args.conflict_questions, args.rng_order, args.dates_v3)
                validate(ep)
                f.write(json.dumps(ep) + "\n")
    (args.out / "value_aliases.json").write_text(json.dumps(aliases))
    meta = {"seed": args.seed, "slots": len(slots), "train_slots": len(train), "val_slots": len(val),
            "test_slots": len(test), "train_subjects": len({s["subject"] for s in train}),
            "val_subjects": len({s["subject"] for s in val}), "test_subjects": len({s["subject"] for s in test}),
            "slots_per_episode": args.slots, "conflict_questions": args.conflict_questions,
            "date_style": args.date_style, "split3": args.split3, "dates_v3": args.dates_v3}
    (args.out / "meta.json").write_text(json.dumps(meta, indent=2))
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
