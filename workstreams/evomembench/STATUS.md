# EvoMemBench Research Agent

**Area:** Memory & Continual Learning
**Source:** https://github.com/Vedant2100/evo-mem-bench
**Owner agent:** `evomembench`
**Current agent state:** CONFIGURED, NOT YET DISPATCHED (no active session or actual model run assumed)

## Research aim
Identify which prior-experience memory methods help a competent frozen agent on held-out tasks.

## Next decisive action
Test no-memory/playbook competence and headroom; run matched core arms before expensive full matrix.

## Experimental gate
No-memory at least 55% overall, 30% per category, meaningful positive control and valid held-out protocol.

## Do not overclaim
Synthetic hidden-rule task is not official ALFWorld; CI green is not actual benchmark evidence.

## Evidence handoff
No master-repo independent agent handoff yet. After dispatch, include immutable source commits, commands, exact per-episode evidence, model results, matched comparisons, blockers, costs and PR links here.


**2026-11-16 reconciliation:** Qwen hidden-rule control finished (base 8/36, oracle 36/36). Official ALFWorld partial run completed 15 episodes (no memory 3/6, static playbook 5/6, BM25 2/3), then failed on reset. Cleanup and 25-reset stress workflow committed; execution and full official evaluation remain unverified. https://github.com/Vedant2100/evo-mem-bench/blob/main/reports/2026-11-09-qwen-memory-results.md
