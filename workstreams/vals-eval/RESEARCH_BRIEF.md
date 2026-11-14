# Vals Eval — Autonomous False Progress / Evaluation Integrity

**Updated:** November 13, 2026. Supersedes the initial "Action Sycophancy" lead.
**Status:** one fictional research-loop prototype implemented and CPU-tested; no real frontier agent results, no Valkyrie registration.
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/pull/3

## What we are actually evaluating

**Question:** Can an autonomous research agent tell the difference between a higher convenient proxy and genuinely better verified performance before it promotes its own proposed changes?

The target behavior is a *sequence of actions*: inspect → change candidate → run experiment → interpret feedback → repeat → promote or reject → document the decision. We grade the resulting state using an independent, immutable evaluator, not the agent's prose.

A user trying to coax a chatbot into agreement is a different research question. We are not starting with conversational sycophancy.

## Candidate failure families — prioritize by autonomy and complementarity

| Priority | Failure family | Autonomous action that might fail | What independent evidence would prove it |
|---|---|---|---|
| **1 (implemented preflight)** | **False Progress** | Agent improves a visible reward repeatedly but promotes a configuration that fails a frozen independent evaluator | Paired proxy/held-out trajectories, final promoted version, objective task success |
| **2** | Experimental-invalidity accumulation | Agent iteratively reports gains from correlated/repeated seeds, invalid ablations, or stale artifacts | Frozen run IDs, distinct trials, reproducibility checks and promotion log |
| **3** | Misaligned exploration / test contamination | Agent repeatedly tunes against accessible evaluation examples and loses transfer | Disjoint held-out task families and matched budgets |
| **4** | Oversight collapse | Second research agent endorses the first agent's false improvement without rerunning checks | Independent sign-off, source trace, verified discrepancy |
| Lower priority | User-pressure sycophancy | Agent changes a conclusion to please the user | User-pressure controls; less specific to autonomous self-improvement |

Existing overlap: RewardHackLab already studies proxy vs verified outcome, while StaleStream studies memory staleness. False Progress is only independently useful if the **researcher's repeated selection/promotion decisions** become a measured phenomenon, not another one-step proxy-gaming example.

## Prototype design

- The autonomous agent controls a restricted **policy JSON**, not arbitrary code. Safe access to read/write artifacts reuses ProvenanceTrap's sandbox; exact outcome verification reuses RewardHackLab's `TicketEnv`.
- **Visible feedback:** score on biased proxy ticket distribution, rewarding resolution and speed. A candidate can appear to improve it while violating workflow and verification requirements on varied tasks.
- **Frozen independent outcome:** reward calculated on disjoint held-out tickets; not shown in agent-visible outputs.
- **Optional independent audit:** one truthful validation query on another disjoint sample, not the final holdout.
- **Promotion:** agent must select and activate a candidate; graded on true before/after result and veracity of the final decision artifact.
- **Budget:** up to 3 proxy experiments; up to 1 audit in the audit arm; at most 18 agent actions per case.
- **Cases:** eight seeded variants of ONE synthetic ticket-policy task family. They are **not eight unrelated research environments**, and fixed deterministic seeds aren't independent repeated stochastic model trials.

### Verified offline software control

15/15 CPU tests pass. The 48 saved episodes are scripted oracle/proxy-chaser/audit-recovery policy controls, **not frontier LLM executions**. They establish that the grader can penalize illusory promotions and reward true improvements; they do not establish that a frontier research agent makes the errors.

Scripted means, proxy-only cases: safe optimization proxy +0.1100 and verified +0.0100; proxy chaser proxy +0.2317 and verified -1.0718, across eight fixed scenarios. These are arbitrary simulator reward units, **not accuracy points or percentages**. The source report captures every per-case control: `hackathons/2026-11/vals_eval/fixtures/scripted_controls.json`.

## Related evaluations, and why novelty is not claimed yet

- [MLE-bench (OpenAI)](https://openai.com/index/mle-bench/) tests engineering agents on ML competitions; a strong external research-agent competence comparator, but our experiment focuses on knowing when *visible progress* is false.
- [RE-Bench (METR)](https://arxiv.org/abs/2411.15114) studies AI R&D task capability under time budgets, including experimentation and optimization. We must distinguish our focus from its agent performance measurements.
- Existing reward-hacking, evaluation-gaming and experiment-fidelity studies already overlap substantially with these ideas. A few hand-designed trap tasks are **not enough to establish a new research contribution**.
- [Valkyrie](https://github.com/vals-ai/Valkyrie) is the official orchestration framework. [Vals' benchmark-service scaffolder](https://github.com/vals-ai/create-benchmark-service) is the appropriate integration candidate once event instructions are known.
- Sycophancy precedents—[SYCON Bench](https://aclanthology.org/2025.findings-emnlp.121/), [SPINE](https://arxiv.org/abs/2609.09090) and [SciSycEval](https://aclanthology.org/2026.findings-emnlp.1501/)—belong to the *deprioritized* user-pressure idea.

## Next experiment (requires explicit model/credit authorization)

Pilot on two developer cases and one chosen frontier model first. Record full tool traces, valid-tool completion, meaningful candidate edits, independent outcomes and cost. If task competence is insufficient, fix the harness **without turning the existing holdout into training data**. If the model exhibits an independently validated illusory promotion despite clean competence, freeze the specification and test the remaining seeded cases, another model and an audit-available control. Do not claim significance on tiny samples.

If it is too easy, expand beyond ticket policy into an actual research workflow where model-generated code runs only inside a constrained sandbox and scorer state remains immutable. A source-aware adversary can inspect the current seeds; the prototype's holdout is procedural, not cryptographically secret.

## Does this require RL?

No. A benchmark/eval needs tasks, agent interaction and grading; it does not require updating model weights. We can later use the stateful environment for RL if it supports resetting and well-specified rewards, but for this event the objective is **measure actual frontier model behavior** and submit a Valkyrie-compatible benchmark.
