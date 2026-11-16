# TrustVal (Vals AI Build Your Own Eval)

**Track:** RL Post-Training & Reward Design (evaluation lane)  
**Canonical source:** https://github.com/Vedant2100/trustval (since 2026-11-15; the copy in `workstreams/vals/` is frozen history)  
**Event:** Vals AI hackathon, Build Your Own Eval track  
**State:** four-task benchmark implemented, published to Valkyrie and evaluated across model generations  
**Decision:** current benchmark-execution cycle complete; external event submission not verified

## Research question

When a state-changing tool call has an ambiguous outcome (commit-then-timeout, stale read, partial batch, duplicate delivery), does a frontier agent inspect authoritative state and recover with exactly-once effects, or does it duplicate or drop side effects?

## Verified evidence

The v3 design was committed before model runs; the naive policy scored 0/4 and the reference solution 4/4.

Ten runs per model:
- Claude Haiku 4.5: 19/40.
- Claude Sonnet 4.6: 35/40 (run-level permutation p=2.3e-4 versus Haiku 4.5).
- Claude Haiku 5.5: 39/40.
- Claude Sonnet 5.5: 40/40.
- Claude Opus 5.5: 40/40.
- GPT-5.3-Codex: 34/40.
- GPT-5.4: 40/40.

Three GPT-6 variants each passed 4/4 in one run apiece; treat those as pilots, not powered model comparisons. The Claude 4.x failures were blind retries of committed writes; Claude 5.5 produced zero duplicates in 89 errored task-trials. GPT-5.3-Codex duplicated writes in five of ten duplicate-delivery trials; GPT-5.4 passed all 40 task-trials.

## Limitations

Four controlled variants of one capability in a synthetic environment, not four independent contributions or a broad tool-use leaderboard. v3 is saturated for Claude 5.5 and GPT-5.4; GPT-6 has only one run per task. The current evidence does not establish general tool-use safety.

## Submission status

The benchmark and model-evaluation work for the event cycle are complete. An official Vals submission receipt or acceptance record has not been verified in the accessible project evidence. Do not claim external submission or acceptance without that receipt.

See the [canonical results ledger](https://github.com/Vedant2100/trustval/blob/main/RESULTS.md) and [README](https://github.com/Vedant2100/trustval/blob/main/README.md).
