# StaleStream RL Memory Agent

**Area:** Memory & Continual Learning
**Source:** https://github.com/Vedant2100/f26/tree/main/cs258/stalestream
**Owner agent:** `stalestream`
**Current agent state:** CONFIGURED, NOT YET DISPATCHED (no active session or actual model run assumed)

## Research aim
Learn a bounded memory rewrite policy for changing facts with downstream reader reward.

## Next decisive action
Build timestamp-correct episode generator and fair symbolic/LLM baselines; measure oracle QA and GRPO runtime.

## Experimental gate
Oracle reader at least 90% EM and 20 percentage-point headroom over strongest nonprivileged baseline.

## Do not overclaim
No verified LoRA/GRPO checkpoint yet; do not leak hidden labels or overwrite unrelated coursework.

## Evidence handoff
No master-repo independent agent handoff yet. After dispatch, include immutable source commits, commands, exact per-episode evidence, model results, matched comparisons, blockers, costs and PR links here.
