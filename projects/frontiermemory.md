# FrontierMemory Learning

**Track:** Memory & Continual Learning  
**Experiment source:** https://github.com/Vedant2100/frontiermemory-learning  
**Paper repository:** https://github.com/Vedant2100/frontiermemory-forge-repo  
**State:** paper submitted to FORGE as submission #11 on 2026-11-16  
**Decision:** current paper workstream complete; follow-up studies require a separate scope

## Research question

Does generated memory from prior coding-agent attempts improve held-out task success, and where does the benchmark pipeline erase or distort the benefit?

## Evidence

No memory 6/45; generated memories 7/45, 4/45, 8/45; pooled 19/135 vs 6/45, +0.01/task, p=0.50. Placebo 4/45; read-first 8/45; all-shown 7/45; none-shown 9/45; raw related evidence 9/45. Word2Vec shows a content-sensitive gain.

## Methods and contribution

The paper centers the benchmark audit: matched memory/no-memory evidence, placebo and delivery controls, task-level gains/losses, and demonstrated pipeline issues. It distinguishes measured failures from possible explanations and scopes the local-model result appropriately.

## Limitations

Only 15 tasks; reference solutions fail on four; about eight tasks lack related source history. A pooled null does not prove memory is useless. Generator/blend attempts that timed out are not successful experimental arms. Submission does not imply acceptance.

## Current status

The FORGE paper was submitted as submission #11 on 2026-11-16. The current paper-finalization work queue is complete. Per-task oracle-from-history and Word2Vec ablations are possible follow-up research, not outstanding submission blockers.

See [evidence ledger](../EVIDENCE.md) and [source map](../SOURCE_MAP.md).
