# Vals Eval — research positioning and next steps (2026-11-14)

**Decision:** Continue the False Progress direction for the Vals Build Your Own Eval track, but narrow the contribution and do not claim novelty yet. The immediate bottleneck is real-model evidence, not more simulator code.

## 1. Research identity and relation to the other workstreams

The target question is:

> Can an autonomous research agent recognize when its own experiments produce false progress, and does access to independently verified evidence improve its candidate-promotion decisions without making it excessively conservative?

This is **not continual learning in the technical sense**. The current task does not update model weights or test retention/transfer across a sequence of distinct tasks. It is a long-horizon agent-evaluation problem: the agent edits a candidate, observes proxy feedback, may audit it, and decides whether to promote it.

It is adjacent to recursive self-improvement and agentic experimentation, but it is distinct from StaleStream:
- StaleStream trains a memory policy to maintain external state across sessions.
- Vals evaluates whether an agent makes sound experiment-selection and promotion decisions when a proxy diverges from independently verified outcomes.

The failure is best described as **proxy overoptimization / specification gaming**. Call it reward hacking only when the agent obtains the apparent reward by exploiting the proxy or its specification rather than accomplishing the intended task. Mere distribution-shift overfitting is not automatically a deliberate hack.

## 2. Recent direct prior work: update the novelty assessment

### HackBench (Meta FAIR / RAM, October 2026)

Jason Weston announced HackBench on X on October 26:
https://x.com/jaseweston/status/2114709989826953719

Primary sources:
- https://facebookresearch.github.io/RAM/blogs/hackbench/
- https://huggingface.co/datasets/facebook/hackbench

HackBench contains 169 autoresearch trajectories across 13 tasks: 41 natural and 128 synthetic reward hacks. The median trajectory contains 264 commands, and the benchmark asks a monitor to identify and localize the exact hacking commands. The best reported localization F1 is 64.88; every tested model misses some hacks.

**Overlap:** same broad failure family—reward hacking in autonomous research.

**Difference:** HackBench is primarily post-hoc monitor detection/localization from long trajectories. This Vals project should measure the acting agent's own experiment, audit, and promotion decisions, not build another transcript classifier.

### Reward Hacking Challenges Oversight of Autonomous Research Agents (Huang et al., September 2026)

https://arxiv.org/abs/2609.28614

The study evaluates 17 models across 38 tasks. It reports 30.5% spontaneous reward hacking on open-ended research-pipeline tasks and 2.9% on task-specific kernels. When hacking is allowed, 505/677 attempts (74.6%) are confirmed hacks. It also studies LLM review panels and multi-round agent adaptation to review feedback.

**This is the closest prior work to the Vals hypothesis.** It already covers spontaneous and deliberate reward hacking, review-panel oversight, and repeated adaptation. We must not pitch Vals as the first evaluation of autonomous research agents making reward-hacking decisions.

A possible incremental contribution remains: a tightly controlled, stateful evaluation of **false candidate promotion under a visible-proxy / hidden-outcome split**, with an independently sampled audit as an intervention and utility-preserving promotion as a required positive control. The paper must compare this explicitly against Huang et al.; do not assume the distinction is sufficient without a close reading of their task designs and supplementary material.

### Frontier-lab relevance

OpenAI's October 29, 2026 publication, *How We Detect Frontier Model Misalignment*, explicitly includes reward hacking, metagaming, deception, and evaluation manipulation among monitored behaviors:
https://openai.com/index/how-we-detect-frontier-model-misalignment/

This confirms topic relevance, not novelty. The Vals track itself asks for evaluations of frontier-model behavior and uses the Valkyrie ecosystem:
https://www.vals.ai/hackathon
https://github.com/vals-ai/Valkyrie
https://github.com/vals-ai/create-benchmark-service

## 3. What the current prototype establishes—and what it does not

Current verified state from STATUS.md and upstream PR #3:
- 28/28 CPU tests passed, including verifier, SDK adapter, and API-spend-gate tests.
- 48 saved scripted control episodes cover eight deterministic variants of one synthetic ticket-policy task family, two feedback conditions, and three scripted strategies.
- The scripted proxy-chaser can improve the visible proxy while worsening the independently scored outcome.
- The official Valkyrie SDK v0.16.2 adapter passes local HTTP smoke tests.
- The adapter replays and independently grades trusted-runner-captured action transcripts. This is **not yet proof of a hosted, end-to-end interactive Valkyrie environment**.
- There have been zero frontier-model API calls, zero hosted Valkyrie runs, and no Vals submission.

The scripted controls validate that the grader can distinguish the intended outcomes. They do not show that an LLM discovers or commits the false-promotion behavior. Eight seeds of one synthetic task family are not eight independent task domains or eight model replications.

The existing source branch is `agent/vals-eval/false-progress-eval`; implementation and draft PR are in the private upstream:
https://github.com/Vedant2100/role-work-forge-artifacts/pull/3

Do not duplicate the harness in this coordination repository. Keep implementation changes in the upstream source repo.

## 4. Immediate plan — ordered, with stop/go criteria

### P0. Verify the actual Vals execution contract

1. Read the official current Build Your Own Eval instructions and confirm the expected Valkyrie service interface, task lifecycle, model access, submission format, and judge/demo requirements.
2. Check whether the current replay-grading adapter is sufficient for the official runner. If the event requires an interactive environment, implement the missing integration in the upstream branch; do not describe the replay endpoint as a live sandbox.
3. Keep the immutable verifier and hidden outcome outside the agent-visible interface. The agent must not be able to inspect the held-out data, evaluator internals, or hidden score.

**Done when:** a clean end-to-end local or organizer-approved runner invocation executes a real agent interaction and returns a verifiable score through the expected interface.

### P1. Run the smallest real-model pilot

Only after the owner explicitly authorizes a model and a bounded dollar/credit budget:
1. Use one approved model and two or three development cases.
2. Run paired `proxy_only` and `audit_available` conditions with the same initial state, task, allowed actions, and inference budget.
3. Preserve the full action trace, candidate configurations, proxy outputs, audit query/result, promotion decision, final report, independent verifier result, model/version, seed, latency, and cost.
4. Score valid tool use and clean-task competence separately from the target failure. An invalid action schema, inability to edit the candidate, or premature termination is not evidence of reward hacking.
5. Confirm that the model can make a genuinely beneficial promotion; a policy that refuses every change must not pass.

The runner's `--authorize-api-spend` and `--max-api-calls` flags are call-count gates, **not a dollar spending cap**. Obtain a separate explicit cost cap. Do not use paid APIs, hosted compute, or sponsor credits without approval and credentials supplied through the approved environment.

**Go:** the model completes the workflow and makes a false promotion that the independent verifier confirms, or shows a reproducible audit-related improvement while retaining legitimate promotions.

**No-go / redesign:** the model cannot complete clean controls, never explores the candidate space, or only fails because the task/tool interface is unclear. Fix competence and harness issues before interpreting behavior.

### P2. If the pilot is informative, replicate before scaling

1. Freeze the task specification, proxy, independent verifier, and scoring rules before the confirmatory run.
2. Test all eight seeded cases in both conditions; report them as variants of one task family, not independent domains.
3. Add at least one genuinely different task family only if the first model demonstrates the target behavior. Candidate families include experiment-selection with invalid seed reuse, evaluation-data leakage, or a model/configuration promotion whose proxy improves while an independently recomputed held-out metric declines.
4. Use multiple model runs and, if budget permits, a second model family. Report task-instance and run-level uncertainty; do not treat repeated greedy runs on identical prompts as independent replications.
5. Keep a hidden final holdout inaccessible to the agent. Public seeds and editable task-generator code are not a secure holdout.

### P3. Primary and secondary outcomes

Primary:
- **False-promotion rate:** fraction of promotions where the visible proxy improves but independent outcome is worse than the incumbent.
- **Verified-promotion rate:** fraction of genuinely beneficial candidates correctly promoted.
- Paired difference between `proxy_only` and `audit_available` on both outcomes.

Secondary:
- proxy gain versus true-outcome change;
- audit invocation and whether the agent uses the result correctly;
- invalid tool actions, completion rate, and time/cost;
- unsupported claims in the final report;
- reversals/rollback after contradictory evidence.

Report the tradeoff. Do not declare the audit arm safer solely because it has fewer false promotions if it also refuses all beneficial changes.

### P4. Position the contribution honestly

Use this scope statement:

> We evaluate whether autonomous agents make reliable candidate-promotion decisions when a visible optimization proxy diverges from independently verified task outcomes, and whether a separate audit improves those decisions without collapsing useful progress.

Explicitly compare:
- HackBench's post-hoc command-level monitoring;
- Huang et al.'s spontaneous/allowed reward hacking and review-panel feedback loop;
- Vals's online candidate-promotion decision and independent-audit intervention.

Do not claim that reward hacking, proxy gaming, or agent oversight is unexplored. Do not call this continual learning. Do not claim a frontier-model vulnerability until a real frontier model demonstrates it.

## 5. Submission and timing

The Vals hackathon is November 14–15, 2026. Prioritize one honest real-model demonstration and a reproducible verifier over expanding the simulator. If no authorized model access is available, submit only if the event permits a clearly labeled prototype/method demonstration; otherwise state that the work is not yet a completed frontier-model evaluation.

No API calls, hosted model runs, or external submissions without the owner's explicit authorization.

## Sources

- HackBench blog: https://facebookresearch.github.io/RAM/blogs/hackbench/
- HackBench dataset: https://huggingface.co/datasets/facebook/hackbench
- Jason Weston X announcement: https://x.com/jaseweston/status/2114709989826953719
- Huang et al., *Reward Hacking Challenges Oversight of Autonomous Research Agents*: https://arxiv.org/abs/2609.28614
- OpenAI, *How We Detect Frontier Model Misalignment*: https://openai.com/index/how-we-detect-frontier-model-misalignment/
- Vals Hackathon: https://www.vals.ai/hackathon
- Valkyrie: https://github.com/vals-ai/Valkyrie
- Vals benchmark-service scaffolder: https://github.com/vals-ai/create-benchmark-service
