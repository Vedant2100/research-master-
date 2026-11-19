# EvoMemBench Research Agent

**Area:** Memory & Continual Learning  
**Source:** https://github.com/Vedant2100/evo-mem-bench  
**Owner agent:** `evomembench`  
**Current state:** ACTIVE / CONDITIONAL — partial official ALFWorld pilot; lifecycle and worker-competence gates not yet cleared

## Research aim

Identify which prior-experience memory methods help a competent frozen agent on held-out tasks.

## Completed evidence

### Synthetic hidden-rule diagnostic (separate from ALFWorld)

On 36 downstream questions, no-memory scored 8/36 and the true prior-discovery oracle 36/36. Extended methods were compared on a matched 24-question subset: no memory 3/24, unrelated random history 4/24, bounded recent history 10/24, non-contextual UCB 15/24, reward-labelled BM25 23/24, and raw/success-only/locally written concise memory with BM25 24/24. This is single-turn synthetic lookup/transfer; top-method differences are not statistically resolvable at this sample size.

### Official ALFWorld partial pilot

Qwen2.5-7B-Instruct, Modal T4, original ALFWorld evaluator, 12 action rounds. Fifteen episodes were saved:

- No memory: 3/6 (50%); all six tasks completed.
- Fixed category playbook: 5/6 (83.3%); static instructions, not learned memory.
- BM25 retrieval: 2/3 (66.7%); only three episodes completed, not a matched six-task comparison.

The completed BM25 subset showed no retrieval advantage over no memory. This is not the full official benchmark or a significant result.

## Current blockers

1. On the sixteenth task, `POST /reset` returned a response without an observation after 15 saved episodes, raising `KeyError('observation')`.
2. A source patch adds explicit `POST /close` cleanup and surfaces server errors. A 25-reset CPU-only stress workflow was added, but a successful run has not been verified.
3. No-memory success is 50%, below the preregistered 55% overall competence gate.

Preserve existing traces and memory banks; do not recompute completed episodes. Do not launch the unfinished BM25 tasks until lifecycle and competence gates pass.

## Next decisive action

Verify the 25-reset stress workflow. Then improve or replace the worker and re-establish no-memory competence without changing the frozen evaluation after observing treatment results. Resume only the three unfinished BM25 tasks if the gates pass.

## Do not overclaim

The hidden-rule diagnostic is not ALFWorld. The playbook is not learned cross-episode memory. The six-task pilot cannot establish significance or generality. CI success is not model-result evidence.

## Evidence handoff

See [canonical report](https://github.com/Vedant2100/evo-mem-bench/blob/main/reports/2026-11-09-qwen-memory-results.md) and [workflow](https://github.com/Vedant2100/evo-mem-bench/blob/main/.github/workflows/alfworld-cpu-preflight.yml).
