# RL Post-Training & Reward Design

**ACTIVE every week.** This area requires actual evidence-backed advancement, not a link collection.

## [RewardHackLab / Lexsi](../projects/rewardhacklab.md)
- **Current state:** completed SFT pilot, no RL run
- **Priority:** CONDITIONAL—fix execution first
- **Next:** Repair tool-call execution to get nonzero baseline, then try real RL; submit honest Lexsi Stage 1 packet by Nov 15 AoE if feasible.
- **Stop/go:** SFT NOT GRPO/RL. Decreasing loss is not useful state improvement; no proxy-vs-verified RL experiment yet.

## [Vals AI Benchmaxxing](../projects/vals.md)
- **Current state:** registration approved, event not run
- **Priority:** HIGH time-boxed
- **Next:** Prepare benchmark and training environment, attend if practical, run baseline→training→eval, preserve code and evidence; avoid spawning an unrelated permanent repo.
- **Stop/go:** Not a codebase or completed result; must check exact official competition rules and avoid overfitting.

**Cross-project rule:** Avoid duplicated experiments. Preserve a distinct falsifiable causal question and controls.

## [Adaptive Test-Time Compute (TTC)](../projects/adaptive-ttc.md)
- **Current state:** hypothesis / incubation; no verified TTC-specific trained model or results.
- **Priority:** CONDITIONAL pilot, worth testing because of long-horizon agentic RL fit; no significant GPU investment until a competence and compute-headroom check passes.
- **Question:** can a persistent RL compute-allocation policy learn from prior tasks, then transfer to held-out task families at matched token, latency and tool budgets?
- **Next:** reuse existing terminal/tool evaluation source, audit the [Atlas](https://frontier-rl-project-atlas-2711vedant-6531.vercel.app/) and prior work, run an honest cheap cost/utility diagnostic. [Owner issue #10](https://github.com/Vedant2100/research-master-/issues/10).
- **Stop/go:** stop if heuristics or per-task routers already saturate the compute-quality Pareto frontier, if the model cannot solve tasks, or if transfer disappears.
