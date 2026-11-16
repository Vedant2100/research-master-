# Memory & Continual Learning

**Two workstreams remain active or conditional; one paper cycle is complete.** Keep evidence-backed advancement distinct from a list of ideas.

## [FrontierMemory Learning](../projects/frontiermemory.md)

- **Current state:** FORGE submission #11 submitted 2026-11-16; current paper work queue complete.
- **Priority:** closed for this paper cycle.
- **Next:** no outstanding submission task. Per-task oracle-from-history and Word2Vec ablations would be a separate follow-up study.
- **Limits:** 15 tasks; four reference solutions fail; about eight tasks lack related source history; pooled null is not proof memory is useless.

## [EvoMemBench](../projects/evomembench.md)

- **Current state:** synthetic hidden-rule diagnostic complete; official ALFWorld pilot has 15 saved episodes and an unresolved reset/lifecycle blocker.
- **Priority:** conditional; competence gate not passed (no-memory 3/6 = 50%, below 55%).
- **Next:** verify the 25-reset stress workflow, then establish worker competence before resuming the three unfinished BM25 tasks.
- **Limits:** hidden-rule tasks are not ALFWorld; playbook is static; small pilot cannot establish significance or generality.

## [StaleStream / CS258](../projects/stalestream.md)

- **Current state:** design and preregistration only; no trained writer or validated environment.
- **Priority:** high course deliverable.
- **Next:** timestamp-correct generator, disjoint held-out episodes, nonprivileged baselines, oracle QA >=90%, >=20 pp headroom and measured 20-step runtime before RL.
- **Limits:** memory update is not continual weight learning; reader transfer and injection robustness remain unproven.

**Cross-project rule:** avoid duplicated experiments. Preserve a distinct falsifiable question, source of truth and controls.
