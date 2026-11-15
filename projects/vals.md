# TrustVal (Vals AI Build Your Own Eval)

**Track:** RL Post-Training & Reward Design (evaluation lane)
**Source:** [`workstreams/vals/`](../workstreams/vals/) in this repo (imported 2026-11-14 from role-work-forge-artifacts @ `be8f2eb`, PR #4)
**Event:** https://www.vals.ai/hackathon, Build Your Own Eval track
**State:** executed on Valkyrie (v3: Haiku 4.5 6/12, Sonnet 4.6 10/12); not yet submitted
**Decision:** HIGH, time-boxed to the Nov 14–15 event

## Research question
When a state-changing tool call has an ambiguous outcome (commit-then-timeout, stale read, partial batch, duplicate delivery), does a frontier agent inspect authoritative state and recover with exactly-once effects, or does it duplicate or drop side effects?

## Existing evidence
Four Harbor tasks with a sidecar SQLite service and hidden verifiers. v2 was saturated (both models 4/4; faults leaked the outcome). v3 (neutral 504/502 errors, non-idempotent writes, preregistered in DESIGN_V3.md): Haiku 4.5 6/12, Sonnet 4.6 10/12 over 3 runs; every failure was a blind retry of a committed write, 2 ended in false success claims. Details: workstreams/vals/RESULTS.md.

## Methods / comparisons
Valkyrie `claude_code-v1.0.0` harness, `anthropic/claude-sonnet-4-6`, Modal provider, one trial per task at concurrency 1 first; inspect full traces; separate infrastructure failures from agent failures.

## Limitations and unproven claims
Four controlled variants of one capability, synthetic environment, not a powered leaderboard. Difficulty is a hypothesis until real traces show failures; if Claude solves everything, report that.

## Next decisive action
Owner review and Vals submission entry. See [STATUS](../workstreams/vals/STATUS.md).

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).
