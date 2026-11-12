# Evidence ledger: actual results versus plans

## [FrontierMemory Learning](projects/frontiermemory.md)
**Verified/source-reported:** No memory 6/45; generated memories 7/45, 4/45, 8/45; pooled 19/135 vs 6/45, +0.01/task, p=0.50. Placebo 4/45; read-first 8/45; all-shown 7/45; none-shown 9/45; raw related evidence 9/45. Word2Vec shows content-sensitive gain.
**Interpretation limits:** Only 15 tasks, broken reference solutions for 4; ~8 tasks lacking related source history; no pooled gain ≠ proof memory useless. Generator attempts timed out and exploratory arms must be separately labeled.

## [EvoMemBench](projects/evomembench.md)
**Verified/source-reported:** Official CROSSEP-EMB ALFWorld harness with pinned upstream. Full-arm branch includes retrieval, UCB/LinUCB, reflection, consolidation, structured state, evolutionary selection, native adapters. Exploratory hidden-rule diagnostic: no memory 16/36, Reflexion 26/36, UCB 22/36, LinUCB 21/36; heating 0/6. CI green is not model-result evidence.
**Interpretation limits:** Planned full ~24,090 episode matrix not confirmed complete; synthetic hidden-rule tasks are NOT official ALFWorld; heldout vs sequential online protocols must not be pooled.

## [StaleStream / CS258](projects/stalestream.md)
**Verified/source-reported:** Design written, scoring/headroom checker exists. No verified trained LoRA writer or validated environment.
**Interpretation limits:** Must compute true state from timestamps not delivery order; no hidden-label exposure; memory update ≠ general recursive learning. Reader transfer and injection robustness unproven.

## [ContagionBench / Swarm](projects/contagionbench.md)
**Verified/source-reported:** 324 logged Qwen2.5-3B synthetic episodes, 9/96 ungated unsafe choices, 6/96 prompt guard, 0/96 applied unsafe under independent gate; gate blocked nine attempted approvals.
**Interpretation limits:** Greedy seed labels repeated cases (3/32,2/32,0/32), fixed source and direct exposure confound multi-hop contagion claims. Swarm entry was not received by organizer.

## [ProvenanceTrap / micro1](projects/provenancetrap.md)
**Verified/source-reported:** 96 Qwen2.5-3B episodes, 22/96 correct target, 20/96 strict safe, 0 unauthorized writes and 2 sensitive-read attempts; 60/76 failures quit before writing.
**Interpretation limits:** Weak tool grounding undermines any claimed safety; grader changed after original run; micro1 submission unverified and deadline missed.

## [RewardHackLab / Lexsi](projects/rewardhacklab.md)
**Verified/source-reported:** Tiny Aya Global 4-bit QLoRA trained 16 steps on 84 examples; HF adapter published; 0/6 verified successes baseline and 0/6 after; all 12 evaluations left state untouched.
**Interpretation limits:** SFT NOT GRPO/RL. Decreasing loss is not useful state improvement; no proxy-vs-verified RL experiment yet.

## [Vals AI Benchmaxxing](projects/vals.md)
**Verified/source-reported:** Ticket confirmed Nov 9 for Nov 14–15 at 660 Alabama St, San Francisco; no model/eval/award yet.
**Interpretation limits:** Not a codebase or completed result; must check exact official competition rules and avoid overfitting.

## [Terminal DreamGym](projects/terminal-dreamgym.md)
**Verified/source-reported:** Preregistered matched evaluation, 2026-11-12 (Qwen2.5-7B, 100 tasks × 3 seeds, equal attempts): handwritten skills − no skill = +0.060 strict success, 95% CI [−0.028, +0.151]; placebo − no skill +0.018; all 1,200 runs re-scored from sandboxes. The July demo's gain came with 3× the baseline's attempts; the "two-seed sweep" was unit-test mock data, not a model run.
**Interpretation limits:** Skills are fixed handwritten text, so this is not a self-improvement test. Held-out tasks share repos with train tasks; low power (9 of 19 base tasks tie).

## [Iterate AI Research Hack](projects/iterate.md)
**Verified/source-reported:** Event Nov 14–15. DreamGym existing repository is candidate; no evidence of accepted registration, attendance or official submission.
**Interpretation limits:** Overlaps Vals; do not claim both attended or a general recursively self-improving agent.

**Claim labels:** proposed, implemented, executed, replicated, externally submitted, accepted. Do not infer one from another; source repository linked from each project card.

## [Adaptive Test-Time Compute (TTC)](projects/adaptive-ttc.md)
**Status — conceptual only:** Earlier conversations proposed learning an agent's inference-time budget policy over repeated long-horizon tasks and measuring cost, transfer, retention and delayed reward. The referenced [Frontier Agent Learning Atlas](https://frontier-rl-project-atlas-2711vedant-6531.vercel.app/) is deployed and marked READY by Vercel on Nov 11, but its source HTML was truncated by the available reader. No dedicated TTC code, trained policy, compute savings, or held-out results have been verified. The new TTC agent and workstream are coordination files, not an executed experiment.

**Existing scientific evidence from others (not our results):** [Learning When to Plan](https://arxiv.org/abs/2509.03581) uses SFT+PPO to learn planning choices in sequential agents; [Learning When to Think](https://arxiv.org/abs/2608.20256) uses GRPO to choose reasoning effort; [constrained compute allocation](https://arxiv.org/abs/2604.14853) learns cost-limited sample allocation; [When Agents Slow Down](https://arxiv.org/abs/2609.15309) analyzes compute-efficiency breakdowns. TTC novelty must be established relative to these baselines.

**Future proof needed:** compute-sensitive verified task successes, matched tool/token/latency budgets, strong heuristic/bandit baselines, an actually learned RL policy, heldout transfer across task families, multiple independent seeds, uncertainty, and provenance. Do not make progress/novelty claims before this evidence exists.
