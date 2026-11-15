# TrustVal (Vals AI Build Your Own Eval)

**Track:** RL Post-Training & Reward Design (evaluation lane)
**Source:** [`workstreams/vals/`](../workstreams/vals/) in this repo (imported 2026-11-14 from role-work-forge-artifacts @ `be8f2eb`, PR #4)
**Event:** https://www.vals.ai/hackathon, Build Your Own Eval track
**State:** implemented, not yet executed on Valkyrie
**Decision:** HIGH, time-boxed to the Nov 14–15 event

## Research question
When a state-changing tool call has an ambiguous outcome (commit-then-timeout, stale read, partial batch, duplicate delivery), does a frontier agent inspect authoritative state and recover with exactly-once effects, or does it duplicate or drop side effects?

## Existing evidence
Four Harbor tasks with sidecar SQLite state service and hidden root verifiers that grade the database snapshot. Structure smoke test passes. No Valkyrie upload and no model run yet.

## Methods / comparisons
Valkyrie `claude_code-v1.0.0` harness, `anthropic/claude-sonnet-4-6`, Modal provider, one trial per task at concurrency 1 first; inspect full traces; separate infrastructure failures from agent failures.

## Limitations and unproven claims
Four controlled variants of one capability, synthetic environment, not a powered leaderboard. Difficulty is a hypothesis until real traces show failures; if Claude solves everything, report that.

## Next decisive action
Authenticate Valkyrie, configure Modal, push dataset, run the first pilot. See [STATUS](../workstreams/vals/STATUS.md).

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).
