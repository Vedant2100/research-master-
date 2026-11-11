# Adaptive Test-Time Compute (TTC) — Experience-Aware Agent Budgeting

**Track:** RL Post-Training & Reward Design  
**Agent:** `adaptive-ttc`  
**Current stage:** RESEARCH DESIGN / INCUBATION — no dedicated experiment implementation, trained policy, or reproduced result has been verified  
**Decision:** WORTH A SMALL VALIDATION PILOT; no new GPU allocation before gates  
**Primary conceptual reference:** [Frontier Agent Learning Atlas](https://frontier-rl-project-atlas-2711vedant-6531.vercel.app/) (owner's deployed artifact; Vercel deployment verified READY 2026-11-11; the source-page reader truncates the HTML, so exact current Atlas text remains unverified)  
**Previous conversations:** adaptive test-time reasoning/search/tool allocation; learning a compute policy across repeated long-horizon agent tasks, plus transfer, retention, compute efficiency and successive learning cycles.

## Hypothesis and the specific research gap

Learn to allocate test-time effort *within an agent's trajectory* conditioned on task state, budget and lessons from **prior tasks**. A persistent policy should distinguish when to act immediately, reason, search/retrieve, verify or stop. Test whether it improves task success at a fixed total budget, or matches quality with less time/tokens/tool use, **including on shifted held-out task families**.

Do not market ordinary per-question difficulty routing or a dynamic plan/no-plan toggle as novel: this problem has significant prior art. The interesting open project-specific question is **cross-episode learning and transfer of compute allocation under verifiable feedback**, not just additional inference tokens or long CoT.

## Proposed MDP and reward (not yet implemented)

- **State:** current observation/task family, recent action success/failure, verifier uncertainty and progress, time/token/tool budget remaining, and policy experience from previous episodes. Avoid final answer, labels, held-out outcomes or privileged state leakage.
- **Action:** small discrete, auditable choices: `act_now`, `short_reason`, `plan_or_replan`, `tool_search_or_verify`, `stop`. The meaning and cost of each must be implemented in an existing harness and measured rather than imagined.
- **Reward:** verified terminal task success minus a precommitted token/latency/tool cost; a budget-constrained formulation should also be reported. Negative utility/safety guardrails can be added if the reused environment already supports them.
- **Persistence:** update the allocation policy across training episodes; freeze weights and any runtime memory before held-out task families. Compare an online-stream setting separately, without pretending online test-task updates are held-out generalization.

## Reuse first — no new generic agent harness

1. [Terminal DreamGym](https://github.com/Vedant2100/terminal_dreamgym): already has a real model, terminal tasks, tool feedback, pytest verifier, curriculum worlds, run traces and budget-relevant decision points. Preferred initial code-reuse inspection.
2. [Role Work Forge artifacts](https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11): already has synthetic tool tasks, state scoring, reward evaluation and experiment orchestration. Private repo: use only if access is available; do not expose code in public master.
3. [EvoMemBench](https://github.com/Vedant2100/evo-mem-bench): existing contextual selection/UCB controls and official ALFWorld harness; valuable methods reference, but current agent-competence concerns make it a risky first TTC testbed.
4. Do NOT duplicate DreamGym, RewardHackLab or EvoMemBench architecture. If reuse reveals that TTC needs a missing module, extend the appropriate original repository on a distinct branch and coordinate with its owner agent.

## Experimental arms (preregister before inference spending)
- **Fixed policy baselines:** always act, always plan, periodic planning, static small/medium/large compute budgets.
- **Strong cheap baselines:** error/uncertainty-threshold and progress-based heuristic, simple budget-aware router, UCB/LinUCB or contextual bandit.
- **Learning baselines:** SFT imitation of an *offline labeled* allocation oracle (not privileged at test time), RL-trained controller such as DQN/PPO depending on action/state form. If a language-model policy is directly optimized, verify it was actually GRPO/PPO and not a prompted selector.
- **Cost control:** same worker model, task IDs, seeds, tool access, allowed wall time, evaluator, and aggregate token/latency/tool budget across compared arms. Report Pareto success–compute fronts rather than only one scalar.
- **Transfer:** held-out task families, shifted difficulty/resource availability and longer trajectories, policy adaptation across many episodes; track retention and forgetting. A single task's extra search is not continual learning.

## Go/no-go gates before serious GPU work
1. Existing environment/test harness executes genuinely verifiable tasks with competent baseline performance and distinct difficulty levels.
2. A paired pilot demonstrates **compute-sensitive headroom**: at least one task cohort benefits meaningfully from extra reasoning/search, and at least one cohort can save cost without degrading success. Otherwise no routing problem exists.
3. Check whether an uncertainty heuristic or simple contextual bandit already reaches the small-budget Pareto front. If yes, RL training is unjustified until a harder but valid control emerges.
4. Freeze a separate held-out stream and cost accounting. Proposed confirmation: >=3 model/evaluation seeds and at least two precommitted budget points, full confidence intervals and negative-transfer audit. Numbers are experiment plans, not achieved results.
5. First decisive target: >=10% median or mean actual compute reduction **at no worse than 2 percentage points of held-out verified task success**, or significantly better success at equal compute, *versus the strongest cheap baseline*, maintained on task-family shift. This is a preregistered proposed gate, not a demonstrated effect.
6. Stop/park if baseline lacks task competence, oracle headroom disappears, improvements vanish under matched budgets, or distribution-shift transfer fails.

## Prior art — direct overlap must be acknowledged

- [Learning When to Plan: Efficiently Allocating Test-Time Compute for LLM Agents](https://arxiv.org/abs/2509.03581) — SFT + PPO policy for when to plan on long-horizon tasks (already very close to dynamic agent planning).
- [Learning When to Think](https://arxiv.org/abs/2608.20256) — GRPO-learned short/long/no-think modes; reported major token savings.
- [Adaptive Test-Time Compute Allocation via Constrained Policy Optimization](https://arxiv.org/abs/2604.14853) — constrained budgeted per-input allocation and learned cheap router.
- [Stop When Enough](https://aclanthology.org/2026.acl-long.1256/) — training-free early stopping with bandit thresholds.
- [When Agents Slow Down](https://arxiv.org/abs/2609.15309) — compute-performance analysis for long-horizon agent sessions.

**Novelty status: unproven.** A credible study must isolate what *experience across tasks* adds beyond an already learned within-task planning policy.

## Milestones

- **Phase 0 — audit:** recover full Atlas source in an authorized reader; inspect original DreamGym/RewardHackLab code and run traces; write a one-page precise overlap map against prior papers.
- **Phase 1 — cheap pilot:** instrument the *existing* terminal/tool evaluator for decision-level token, wall-clock, search and verify costs; run two fixed budgets and a precommitted heuristic on a paired task set.
- **Phase 2 — learning gate:** if headroom exists, train a contextual controller or actual RL policy and evaluate held-out task families under matched budgets.
- **Phase 3 — scientific replication:** 3+ independent seeds, robustness, ablations on prior-task memory/weights, policy persistence and negative transfer; paper only if the learned cross-task contribution survives.

**Owner issue:** [#10](https://github.com/Vedant2100/research-master-/issues/10). **Master evidence:** [EVIDENCE.md](../EVIDENCE.md). **Code reuse:** [SOURCE_MAP.md](../SOURCE_MAP.md).
