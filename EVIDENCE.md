# Evidence ledger: actual results versus plans

**Canonical-source reconciliation: 2026-11-16.** Distinguish completed runs, study closure, benchmark upload, event portal submission and peer-review acceptance; missing receipts do not establish submission.

## [FrontierMemory Learning](projects/frontiermemory.md)
**Verified/source-reported:** No memory 6/45; generated memories 7/45, 4/45, 8/45; pooled 19/135 vs 6/45, +0.01/task, p=0.50. Placebo 4/45; read-first 8/45; all-shown 7/45; none-shown 9/45; raw related evidence 9/45. Word2Vec shows content-sensitive gain.
**Stage:** completed benchmark audit and paper. FORGE submission #11 user-reported Nov 16, but the master contains no independent receipt. [Paper](https://github.com/Vedant2100/frontiermemory-forge-repo); [final experiment record](https://github.com/Vedant2100/frontiermemory-learning/blob/main/FINAL-RESULTS.md).
**Interpretation limits:** Only 15 tasks, broken reference solutions for 4; ~8 tasks lacking related source history; no pooled gain ≠ proof memory useless. Generator attempts timed out and exploratory arms must be separately labeled.

## [EvoMemBench](projects/evomembench.md)
**Verified/source-reported:** Official CROSSEP-EMB ALFWorld harness with pinned upstream. Full-arm branch includes retrieval, UCB/LinUCB, reflection, consolidation, structured state, evolutionary selection, native adapters. Exploratory hidden-rule diagnostic: no memory 16/36, Reflexion 26/36, UCB 22/36, LinUCB 21/36; heating 0/6. CI green is not model-result evidence.
**Additional results:** Qwen2.5-7B hidden-rule positive control: no memory 8/36 vs oracle 36/36; extended methods only on matched 24 questions (BM25 24/24). Original ALFWorld worker pilot: 15 completed episodes, no memory 3/6, static playbook 5/6, BM25 2/3; stopped at POST /reset error. Code for lifecycle close and 25-reset stress is committed, not evidence that a 200-task run completed. [Report](https://github.com/Vedant2100/evo-mem-bench/blob/main/reports/2026-11-09-qwen-memory-results.md).
**Interpretation limits:** Full ~24,090 episode matrix unverified; synthetic hidden-rule tasks are NOT official ALFWorld; online and held-out protocols must not be pooled. The 15-episode official run is a partial, not fully matched BM25 comparison.

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
**Earlier pilot:** Tiny Aya 4-bit QLoRA, 16 SFT steps on 84 examples: 0/6 before and after; subsequent 64-step evaluation had an action-history train/eval mismatch and reported 0/18 in both arms.
**Corrected completed SFT run (2026-11-14):** Shared prompt/dispatch history, 210 supervised steps from 210 teacher actions across 42 training tickets, seed 2026; base 0/18, SFT 18/18 independently state-verified held-out ticket successes, zero forbidden resolutions, four environment calls per SFT evaluation. Competence gate passed. [Exact metrics](https://github.com/Vedant2100/role-work-forge-artifacts/blob/main/hackathons/2026-11/results/modal-run-43647115920/tmp/modal-results/lexsi_tiny_aya_prompt_alignment_2026_11_14/metrics.json); [Actions run](https://github.com/Vedant2100/role-work-forge-artifacts/actions/runs/43647115920).
**GRPO attempt:** Interrupted after 439.4 seconds during proxy arm; first three four-trajectory groups had all-zero rewards and no update. Verified-reward arm and held-out RL comparison were not executed. [Interrupted run](https://github.com/Vedant2100/role-work-forge-artifacts/blob/main/hackathons/2026-11/results/modal-run-43647115920/tmp/modal-results/rewardhacklab_rl/43641448741/run_status.json).
**Interpretation limits:** This is SFT, NOT GRPO/RL. One seed and a narrow ticket template family; do not infer a verified reward optimization benefit. Lexsi portal submission unverified.

## [TrustVal (Vals Build Your Own Eval)](projects/vals.md)
**Verified/source-reported:** Valkyrie runs 2026-11-14, Claude Code harness. v2: Haiku 4.5 and Sonnet 4.6 both 4/4 (saturated: errors leaked the outcome). v3 (preregistered DESIGN_V3.md, oracle 4/4, naive control 0/4): 10 runs per model: Haiku 4.5 19/40, Sonnet 4.6 35/40 (run-level permutation p = 2.3e-4); all 26 failures were blind retries of committed non-idempotent writes; false success reports in 4/21 Haiku and 4/5 Sonnet failures. Claude 5.5 (10 runs each): Haiku 39/40, Sonnet 40/40, Opus 40/40, 0 duplicates in 89 errored task-trials. Local re-grade matches Valkyrie.
**Further completed model runs:** GPT-5.3-Codex 34/40, GPT-5.4 40/40, GPT-6 Astra/Sol/Terra each 4/4 on one v3 pilot. v4 with 30-second delayed visibility: Haiku 5.5 11/12, Sonnet 5.5 12/12, GPT-6.1 Terra 12/12. The canonical [results ledger](https://github.com/Vedant2100/trustval/blob/main/RESULTS.md) records runs and traces. v3/v4 experiments complete; official Vals portal submission not verified.
**Interpretation limits:** Both v3 and v4 largely saturated for current models; per-task rates have wide intervals; four variants of one capability with deterministic faults. One v4 Haiku failure was partly shaped by harness sleep restrictions.

## [Terminal DreamGym](projects/terminal-dreamgym.md)
**Verified/source-reported:** Preregistered matched evaluation, 2026-11-12 (Qwen2.5-7B, 100 tasks × 3 seeds, equal attempts): handwritten skills − no skill = +0.060 strict success, 95% CI [−0.028, +0.151]; placebo − no skill +0.018; all 1,200 runs re-scored from sandboxes. Model-written skills (Qwen writes SKILL.md from its own failures, leave-one-family-out, 5 seeds, 2,000 runs): +0.000 [−0.088, +0.097]. Same loop with qwen3-coder:30b as the writer (7B solver, 2,000 runs): +0.023 [−0.072, +0.118]. New benchmark v2 (52 calibrated tasks in 16 new repos, 1,040 runs, 97.5% repo-cluster CIs): handwritten −0.035 [−0.129, +0.053]; 30B skills −0.100 [−0.187, −0.018]; placebo − no skill −0.065 [−0.157, +0.033]. The July demo's gain came with 3× the baseline's attempts; the "two-seed sweep" was unit-test mock data, not a model run.
**Stage:** four preregistered experiments finished and workstream closed/deprioritized on 2026-11-13. [Source](https://github.com/Vedant2100/terminal_dreamgym).
**Interpretation limits:** One 7B solver; only the simplest self-improvement loop tested (7B and 30B skill writers). Original benchmark: held-out tasks share repos with train tasks, 9 of 19 base tasks tie. v2 fixes these; intervals remain about ±0.09, and the v2 harm is confounded with prompt length (placebo also lower).

## [Iterate AI Research Hack](projects/iterate.md)
**Verified/source-reported:** Nov 14–15 event has ended; owner reported rejection. No evidence of attendance or official submission. Event-specific queue is not pursued, and DreamGym's separate research runs are not Iterate results.
**Interpretation limits:** Overlaps Vals; do not claim both attended or a general recursively self-improving agent.

**Claim labels:** proposed, implemented, executed, replicated, externally submitted, accepted. Do not infer one from another; source repository linked from each project card.

## [Adaptive Test-Time Compute (TTC)](projects/adaptive-ttc.md)
**Status — conceptual only:** Earlier conversations proposed learning an agent's inference-time budget policy over repeated long-horizon tasks and measuring cost, transfer, retention and delayed reward. The referenced [Frontier Agent Learning Atlas](https://frontier-rl-project-atlas-2711vedant-6531.vercel.app/) is deployed and marked READY by Vercel on Nov 11, but its source HTML was truncated by the available reader. No dedicated TTC code, trained policy, compute savings, or held-out results have been verified. The new TTC agent and workstream are coordination files, not an executed experiment.

**Existing scientific evidence from others (not our results):** [Learning When to Plan](https://arxiv.org/abs/2509.03581) uses SFT+PPO to learn planning choices in sequential agents; [Learning When to Think](https://arxiv.org/abs/2608.20256) uses GRPO to choose reasoning effort; [constrained compute allocation](https://arxiv.org/abs/2604.14853) learns cost-limited sample allocation; [When Agents Slow Down](https://arxiv.org/abs/2609.15309) analyzes compute-efficiency breakdowns. TTC novelty must be established relative to these baselines.

**Future proof needed:** compute-sensitive verified task successes, matched tool/token/latency budgets, strong heuristic/bandit baselines, an actually learned RL policy, heldout transfer across task families, multiple independent seeds, uncertainty, and provenance. Do not make progress/novelty claims before this evidence exists.
