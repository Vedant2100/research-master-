# FrontierMemory Research Agent

**Area:** Memory & Continual Learning  
**Experiment source:** https://github.com/Vedant2100/frontiermemory-learning  
**Paper source:** https://github.com/Vedant2100/frontiermemory-forge-repo  
**Owner agent:** `frontiermemory`  
**Current state:** PAPER SUBMITTED — FORGE submission #11, 2026-11-16; current paper-finalization work queue closed

## Completed handoff

The benchmark-audit paper was submitted to FORGE as submission #11. The paper repository and experimental source repository are distinct; see [SOURCE_MAP.md](../../SOURCE_MAP.md). The paper's claims remain scoped to the 15-task audit and its controls.

## Evidence summary

No memory 6/45; generated memory runs 7/45, 4/45 and 8/45; pooled 19/135 vs 6/45, +0.01/task, p=0.50. Placebo 4/45; read-first 8/45; all-shown 7/45; none-shown 9/45; raw related evidence 9/45. Word2Vec shows a content-sensitive gain. The paper distinguishes the measured audit findings from possible explanations and does not treat the pooled null as proof that memory never helps.

## Limitations

Only 15 tasks; reference solutions fail on four; about eight tasks lack related source history. Generator/blend attempts that timed out are not successful experimental arms. Submission is not acceptance.

## Closure

The current task — freeze the evidence, finalize the paper and submit it — is complete. Per-task oracle-from-history and Word2Vec ablations are possible future research, not outstanding submission blockers. Do not keep this work queue marked as an unfinished paper task.

## Provenance

- FORGE submission: #11, 2026-11-16.
- Experimental evidence and raw traces: canonical experiment repository above.
- Paper and submission artifact: canonical paper repository above.
