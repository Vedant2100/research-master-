# TrustVal (Vals AI Build Your Own Eval)

**Track:** RL Post-Training & Reward Design (evaluation lane)
**Source:** [`workstreams/vals/`](../workstreams/vals/) https://github.com/Vedant2100/trustval (canonical since 2026-11-15; the research-master `workstreams/vals/` copy is a frozen snapshot) (imported 2026-11-14 from role-work-forge-artifacts @ `be8f2eb`, PR #4)
**Event:** https://www.vals.ai/hackathon, Build Your Own Eval track
**State:** executed on Valkyrie (v3, 10 runs/model: Haiku 4.5 19/40, Sonnet 4.6 35/40, Haiku 5.5 39/40, Sonnet 5.5 40/40, Opus 5.5 40/40); not yet submitted
**Decision:** HIGH, time-boxed to the Nov 14–15 event

## Research question
When a state-changing tool call has an ambiguous outcome (commit-then-timeout, stale read, partial batch, duplicate delivery), does a frontier agent inspect authoritative state and recover with exactly-once effects, or does it duplicate or drop side effects?

## Existing evidence
Four Harbor tasks with a sidecar SQLite service and hidden verifiers. v2 was saturated (both models 4/4; faults leaked the outcome). v3 (neutral 504/502 errors, non-idempotent writes, preregistered in DESIGN_V3.md): 10 runs per model: Haiku 4.5 19/40, Sonnet 4.6 35/40 (run-level p = 2.3e-4); every failure was a blind retry of a committed write; Sonnet 4.6 reported false success in 4 of its 5 failures. The Claude 5.5 models never duplicated a write (89 errored task-trials): v3 separates generations but is saturated for current models. Details: workstreams/vals/RESULTS.md.

## Methods / comparisons
Valkyrie `claude_code-v1.0.0` harness, `anthropic/claude-sonnet-4-6`, Modal provider, one trial per task at concurrency 1 first; inspect full traces; separate infrastructure failures from agent failures.

## Limitations and unproven claims
Four controlled variants of one capability, synthetic environment, not a powered leaderboard. Difficulty is a hypothesis until real traces show failures; if Claude solves everything, report that.

## Next decisive action
Owner review and Vals submission entry. See [STATUS](../workstreams/vals/STATUS.md).

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).
