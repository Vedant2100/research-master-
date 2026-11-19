# Evidence ledger: actual results versus plans

## [FrontierMemory Learning](projects/frontiermemory.md)

**Status:** The paper was submitted to FORGE as submission **#11 on 2026-11-16**. Paper workstream complete; experiment source and paper source are distinct (see [SOURCE_MAP.md](SOURCE_MAP.md)).

**Verified/source-reported:** No memory 6/45; generated memories 7/45, 4/45, 8/45; pooled 19/135 vs 6/45, +0.01/task, p=0.50. Placebo 4/45; read-first 8/45; all-shown 7/45; none-shown 9/45; raw related evidence 9/45. Word2Vec shows a content-sensitive gain.

**Interpretation limits:** Only 15 tasks, broken reference solutions for 4; about 8 tasks lack related source history; no pooled gain is not proof memory is useless. Generator attempts timed out and exploratory arms must remain separately labeled. Submission does not imply acceptance.

## [EvoMemBench](projects/evomembench.md)

**Verified/source-reported — separate synthetic hidden-rule diagnostic:** On 36 downstream questions, no-memory 8/36 (22.2%) and true prior-discovery oracle 36/36 (100%). The predefined gate excluded seed 33 from extended method comparisons because its no-memory score was 5/12 (41.7%), despite oracle 12/12. On the matched 24 questions from seeds 11 and 22: unrelated random history 4/24, bounded recent history 10/24, non-contextual UCB 15/24, reward-labelled BM25 23/24, and raw/success-only/locally written concise memory with BM25 24/24. This is single-turn synthetic lookup/transfer, not multi-step ALFWorld or general continual learning. The 24-question differences do not resolve a ranking among the top methods.

**Verified/source-reported — official ALFWorld partial pilot:** Original evaluator, Qwen2.5-7B-Instruct on Modal T4, 12 action rounds. No memory 3/6 (50.0%); fixed category playbook 5/6 (83.3%); BM25 2/3 (66.7%). BM25 is incomplete and not a matched six-task comparison; the completed BM25 subset showed no retrieval advantage over no memory. These six tasks do not establish statistical significance or generality.

**Blocker:** After 15 saved episodes, the sixteenth `POST /reset` response lacked an observation and raised `KeyError('observation')`. A cleanup patch adds explicit `POST /close` and exposes server errors; a 25-reset CPU-only stress workflow was added. Its successful execution has **not been independently verified here**, so the three unfinished BM25 tasks remain blocked. The six-task no-memory result is also below the preregistered 55% competence threshold. Preserve existing traces; do not recompute completed episodes.

## [StaleStream / CS258](projects/stalestream.md)

**Verified/source-reported:** Design, preregistration and scoring/headroom checker exist. No verified trained LoRA writer, validated environment, or improvement result.

**Interpretation limits:** Ground truth must be computed from event timestamps, not delivery order; no hidden-label exposure; memory updates are not equivalent to continual weight learning. Reader transfer and injection robustness remain unproven.

## [ContagionBench / Swarm](projects/contagionbench.md)

**Verified/source-reported:** 324 logged Qwen2.5-3B synthetic episodes; 9/96 ungated unsafe choices, 6/96 with prompt guard, and 0/96 applied unsafe actions under an independent state gate; the gate blocked nine attempted approvals.

**Interpretation limits:** Greedy seed labels repeat cases (3/32, 2/32, 0/32); fixed source and direct exposure confound multi-hop contagion claims. The Swarm entry was not received by the organizer. Independent cases/seeds and mediated-vs-direct exposure are still needed.

## [ProvenanceTrap / micro1](projects/provenancetrap.md)

**Verified/source-reported:** 96 Qwen2.5-3B episodes, 22/96 correct target, 20/96 strict safe, zero unauthorized writes and two sensitive-read attempts; 60/76 failures quit before writing.

**Interpretation limits:** Weak tool grounding undermines safety conclusions; the grader changed after the original run. micro1 submission is unverified and its deadline was missed. A model that quits before doing authorized work is not demonstrated safe.

## [RewardHackLab / Lexsi](projects/rewardhacklab.md)

**Verified/source-reported — corrected SFT competence calibration, workflow run 43647115920:** CohereLabs/tiny-aya-global, 4-bit QLoRA, seed 2026, 42 training tasks / 210 teacher action examples / 210 SFT steps. The training manifest separates TKT-0000–0041 from 18 evaluation tasks TKT-0042–0059. Base model: 0/18 verified successes, zero forbidden resolutions; it repeatedly called `lookup_policy` and never reached `finish` or `complete`. SFT: 18/18 verified successes, zero forbidden resolutions, and all five action stages completed. The preregistered competence gate (>=60% held-out verified success, zero forbidden resolutions) passed. This is SFT, **not RL/GRPO**.

**Failed/incomplete RL diagnostic — workflow run 43641448741:** manually interrupted after 439.4 seconds while sampling the proxy-reward arm. The first three training tasks each produced four zero-reward trajectories, so no policy update occurred for those groups. The run never reached the verified-reward arm or held-out evaluation. It is not evidence for either reward hypothesis.

**Next evidence required:** matched proxy-vs-verified reward optimization from the same SFT checkpoint, nonzero reward variance/optimizer steps, held-out verified outcomes, multiple seeds and cost accounting.

## [TrustVal](projects/vals.md)

**Verified/source-reported:** Four Harbor tasks; v3 preregistered before runs, with naive policy 0/4 and reference solution 4/4. Ten runs per model: Claude Haiku 4.5 19/40; Sonnet 4.6 35/40 (run-level permutation p=2.3e-4); Claude Haiku 5.5 39/40; Sonnet 5.5 40/40; Opus 5.5 40/40; GPT-5.3-Codex 34/40; GPT-5.4 40/40. Three GPT-6 variants each passed 4/4 in one run each, which is only a pilot. All 26 Claude 4.x failures were blind retries of committed writes; Sonnet 4.6 reported false success in 4/5 failures. Claude 5.5 produced zero duplicates in 89 errored task-trials. GPT-5.3-Codex duplicated writes in 5/10 duplicate-delivery trials.

**v4 delayed-visibility split:** Three runs each of Claude Haiku 5.5, Sonnet 5.5 and GPT-6.1 Terra. Sonnet and Terra passed 12/12 each. Haiku passed 11/12; its one failure duplicated a payment after the agent's background wait ended and it checked state before the 30-second visibility delay expired. The harness blocks long foreground sleeps, which shaped this failure. The project stopped rather than making the delay invisible, because that would turn the decision into guesswork. v4 is near-saturated for current models, with one observed failure whose interpretation is constrained by the harness.

**Interpretation limits:** Four controlled variants of one capability in a synthetic environment, not a broad tool-use leaderboard. v3 is saturated for Claude 5.5 and GPT-5.4; GPT-6 v3 tests are one run per task. v4 has only three runs per model and is not a powered comparison. The current evidence does not establish general tool-use safety.

**Status:** Benchmark and model-evaluation work for the event cycle are complete. An official Vals submission receipt or acceptance record has not been verified; do not claim external submission or acceptance without it.

## [Terminal DreamGym](projects/terminal-dreamgym.md)

**Verified/source-reported:** Preregistered matched evaluation (Qwen2.5-7B, 100 tasks x 3 seeds, equal attempts): handwritten skills minus no skill = +0.060 strict success, 95% CI [-0.028, +0.151]; placebo +0.018. Model-written skills (leave-one-family-out, 5 seeds, 2,000 runs): +0.000 [-0.088, +0.097]. 30B-written skills: +0.023 [-0.072, +0.118]. Benchmark v2 (52 calibrated tasks in 16 new repos, 1,040 runs): handwritten -0.035 [-0.129, +0.053]; 30B skills -0.100 [-0.187, -0.018] under the preregistered 97.5% interval; placebo -0.065 [-0.157, +0.033]. All runs were re-scored from saved sandboxes.

**Decision:** Deprioritized 2026-11-13. No further runs planned on this loop; the evidence does not justify RL on the current design.

## [Iterate AI Research Hack](projects/iterate.md)

**Status:** Owner declined participation. No confirmed registration, attendance or official submission. This event is closed/not planned; do not treat it as an active opportunity.

## [Adaptive Test-Time Compute (TTC)](projects/adaptive-ttc.md)

**Status — conceptual only:** No dedicated TTC code, trained policy, compute savings or held-out results verified. The Atlas deployment is a conceptual reference, not evidence of an executed TTC experiment. The agent/workstream files are coordination records only.

**Future proof needed:** compute-sensitive verified task success, matched token/latency/tool budgets, strong heuristic and bandit baselines, an actually learned policy, held-out task-family transfer, multiple seeds, uncertainty and provenance.

**Claim labels:** proposed, implemented, executed, replicated, externally submitted, accepted. Never infer one from another.
