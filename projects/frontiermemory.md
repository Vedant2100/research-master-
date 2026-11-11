# FrontierMemory Learning

**Track:** Memory & Continual Learning  
**Source:** https://github.com/Vedant2100/frontiermemory-learning  
**State:** executed official-style audit, drafted paper  
**Decision:** HIGH—finish paper

## Research question
Does generated memory from prior coding-agent attempts improve held-out task success, and where does the pipeline erase the benefit?

## Existing evidence
No memory 6/45; generated memories 7/45, 4/45, 8/45; pooled 19/135 vs 6/45, +0.01/task, p=0.50. Placebo 4/45; read-first 8/45; all-shown 7/45; none-shown 9/45; raw related evidence 9/45. Word2Vec shows content-sensitive gain.

## Methods / comparisons
Official pipeline, matched attempts, preregistered analysis, placebo, memory exposure, corpus access audit, hidden-test partial credit, grader/harness diagnosis.

## Limitations and unproven claims
Only 15 tasks, broken reference solutions for 4; ~8 tasks lacking related source history; no pooled gain ≠ proof memory useless. Generator attempts timed out and exploratory arms must be separately labeled.

## Next decisive action
Finalize latest generator/blend arm and artifact, freeze figures, decide FORGE Nov 15 submission and save receipt; then per-task oracle-from-history and Word2Vec ablations.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).