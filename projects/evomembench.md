# EvoMemBench

**Track:** Memory & Continual Learning  
**Source:** https://github.com/Vedant2100/evo-mem-bench  
**State:** partial official ALFWorld model pilot plus separate synthetic hidden-rule diagnostic  
**Decision:** CONDITIONAL — lifecycle and worker-competence gates first

## Research question

When does prior experience improve a capable frozen agent's later tasks, and which external-memory mechanisms matter?

## Existing evidence

**Synthetic hidden-rule diagnostic:** 36 downstream questions; no-memory 8/36 (22.2%), true prior-discovery oracle 36/36. On the matched 24-question subset from seeds 11 and 22, no-memory 3/24, unrelated random history 4/24, bounded recent history 10/24, non-contextual UCB 15/24, reward-labelled BM25 23/24, and raw/success-only/locally written concise memory with BM25 24/24. This is single-turn lookup/transfer, not multi-step ALFWorld or general continual learning. The 24-question sample cannot resolve differences among top methods.

**Official ALFWorld pilot:** 15 episodes were saved using the original evaluator and Qwen2.5-7B-Instruct on Modal T4, with 12 action rounds. No memory completed 3/6 tasks (50%); a fixed category playbook completed 5/6 (83.3%); BM25 completed 2/3 (66.7%). BM25 did not show a measured retrieval advantage on its three completed matched tasks. This is a small, incomplete pilot, not the full benchmark.

## Current blocker

The sixteenth game's reset returned a response without an observation after 15 episodes, raising `KeyError('observation')`. A patch now adds explicit `POST /close` cleanup and exposes server errors. A 25-reset CPU-only stress workflow was added, but its successful run has not been verified. Preserve the 15 saved episodes and memory banks; do not recompute them.

The six-task no-memory score (50%) is below the preregistered 55% overall competence threshold. The playbook result is encouraging but too small to establish general competence.

## Methods and remaining work

No-memory, fixed playbook, random/recent, BM25, success/outcome labels, UCB/LinUCB, Reflexion, ExpeL, Letta-inspired consolidation, A-MEM, ReasoningBank, ACE and distinct parameter-learning methods remain relevant comparisons. The full ~24,090-episode matrix is not complete.

## Next decisive action

1. Verify the 25-reset lifecycle stress workflow.
2. Diagnose/improve the worker's no-memory competence without changing the frozen evaluation after seeing treatment outcomes.
3. Resume only the three unfinished BM25 tasks if lifecycle and competence gates pass.
4. Expand to held-out/online protocols, multiple memory-building seeds and the full method matrix only after the pilot justifies it.

CI success is not benchmark evidence; synthetic hidden-rule results must never be reported as official ALFWorld results.
