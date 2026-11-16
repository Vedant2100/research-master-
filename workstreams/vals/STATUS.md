# TrustVal (Vals AI Build Your Own Eval)

**Area:** RL Post-Training & Reward Design (evaluation lane)  
**Event:** Vals AI Build Your Own Eval, Nov 14–15 2026  
**Owner agent:** `vals`  
**Canonical source:** https://github.com/Vedant2100/trustval (since 2026-11-15)  
**Current state:** benchmark implemented, published to Valkyrie and evaluated across model generations; current execution queue closed

## Canonical-source rule

All further TrustVal code, results and maintenance live in [Vedant2100/trustval](https://github.com/Vedant2100/trustval). This directory is a frozen historical snapshot. Do not edit it as a second canonical copy or revive the discarded earlier implementation.

## Completed benchmark and evaluations

- Four Harbor tasks with independent SQLite-state verifiers.
- v3 preregistered before model runs; naive policy 0/4, reference solution 4/4.
- Ten runs per model: Claude Haiku 4.5 19/40; Sonnet 4.6 35/40; Haiku 5.5 39/40; Sonnet 5.5 40/40; Opus 5.5 40/40; GPT-5.3-Codex 34/40; GPT-5.4 40/40.
- Three GPT-6 variants each passed 4/4 in one run apiece; these are pilots, not powered comparisons.
- All 26 Claude 4.x failures were blind retries of committed writes. Claude 5.5 had zero duplicates in 89 errored task-trials.

See the canonical [RESULTS.md](https://github.com/Vedant2100/trustval/blob/main/RESULTS.md) for run IDs, per-task results, statistical tests, traces and limitations.

## Submission status

The benchmark implementation and current model-evaluation cycle are complete. An official Vals submission receipt or acceptance record has not been verified in accessible evidence. Do not claim submission or acceptance without the receipt.

## Closure

The original work queue — prepare and execute a reproducible Vals benchmark attempt — is complete. Any future v4 or new model-generation evaluation should be a separately scoped project with its own protocol and issue.
