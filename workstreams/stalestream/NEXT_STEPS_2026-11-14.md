# StaleStream — next research steps (2026-11-14)

**Read this before continuing the run.** This note supersedes the stale ordering in the older HANDOFF work queue where it conflicts. Keep STATUS.md as the factual evidence log; preregister each new run there before launch.

## Executive decision

Continue StaleStream, but do not broaden it into a generic continual-learning benchmark or a reward-hacking project.

The defensible research framing is:

> **RL-trained maintenance of bounded external memory across sequential sessions, where facts become stale, conflict, or depend on information elsewhere in the stream.**

This is a continual-learning-adjacent problem: the agent accumulates and revises persistent experience over time. It is not parameter-level continual learning yet. The current system trains an extractor/writer while the downstream reader is frozen.

The strongest current result is GRPO on the 1.7B line-level extractor: test EM 0.691 ± 0.011 across three seeds, versus 0.259 for the untrained extractor. However, the gain is primarily relation-label validity (0.63 → 0.97); date accuracy moves only 0.68 → 0.70, and cross-referenced dates remain the weakest category (0.57 test EM). **[2026-11-15 correction: the 0.68 → 0.70 date figure was a broken metric (relative/cross-referenced dates were always scored wrong). With stream-resolved gold dates, GRPO raises date-driven conflict resolution 0.69 → 0.83; see STATUS.md CORRECTION.]** Do not describe this as a demonstrated solution to stale-fact reasoning until targeted conflict/date metrics improve.

The v3 gate is a **marginal pass**: oracle 0.997, strongest non-privileged baseline 0.783, point-estimate gap 0.214, paired-bootstrap 95% CI [0.194, 0.234]. The point estimate passes the fixed 0.20 threshold; the interval straddles it. Do not hide that qualification or change the threshold.

## Priority 0 — finish and preserve the currently preregistered run

1. Check whether `scripts/extractor_round2.sh` is still running. If it is, let it finish; do not restart or alter its configuration. It was preregistered to run session-context GRPO for seeds 0, 1, and 2 after the offline RFT/DPO arms.
2. Its output directory is `$S/runs/extractor_round2/`. Preserve `progress.log`, `ctx_s{0,1,2}.log`, each `ctx_s*/train_log.jsonl`, checkpoints, `mem_*_{val,test}.jsonl`, and `eval_*_{val,test}.jsonl`, plus bank-generation/scoring/build logs and files.
3. Report all three seeds, validation and test EM, paired-bootstrap differences against the header-context GRPO extractor, per-tag EM, `fact_date_ok`, relation/value/subject/date extraction accuracy, and memory length. The preregistered primary comparison is seed-mean test EM against header-context GRPO; secondary outcomes are per-tag and date metrics.
4. If the run is already complete, audit the output files and recompute the reported numbers before starting another training job.

## Priority 1 — make the DPO comparison scientifically fair

### Objective: keep the reward identical

GRPO, RFT, and DPO must all use the same frozen downstream Qwen3-4B reader exact-match reward on the same resolved-memory pipeline. Do not substitute relation-validity or extraction-format reward for DPO.

DPO does not consume the scalar reward directly: the reward is used to construct preferred/rejected pairs. GRPO uses relative scalar rewards within sampled groups; RFT uses high-reward completions as supervised targets. The objective being optimized should remain the same downstream reader success.

The current extractor DPO bank already follows this principle: `bank_extract.py score` scores candidate memories with the reader, and `bank.py build` selects the best/worst same-prompt candidates when the reader-reward gap is at least 1/6.

### Why the current result is not a fair algorithm ranking

- The extractor bank has 26,044 line groups and 208,352 candidate samples, but only 8.8% of groups have reward variance.
- This yields 2,294 RFT examples and 2,294 DPO pairs; mean DPO reward gap is 0.19.
- DPO is one seed, trained with the writer arm's untuned settings (beta 0.1, learning rate 1e-6, one epoch).
- The bank is generated from the base extractor (off-policy). GRPO samples from the evolving policy (on-policy) and has three seeds.
- Thus the current GRPO–DPO gap mixes algorithm, data-distribution, hyperparameter, and seed-count effects.

### Required follow-up

A. **Tune offline DPO on validation only.** Use a small preregistered grid over beta, learning rate, and epochs. Keep the test set untouched. Report preference-pair count, reward-gap distribution, tie/variance rate, train loss, and validation reader EM for every setting. Do not choose settings from test results.

B. **Run iterative/on-policy DPO.** After an initial DPO update, sample new same-prompt candidate groups from the current DPO policy, score every candidate with the same frozen reader reward, rebuild chosen/rejected pairs, and train the next round. Keep the reward, memory resolver, train split, and total compute budget fixed. Report offline DPO and iterative DPO separately.

C. **Use at least three seeds for the selected DPO configuration.** Compare against the three-seed GRPO result. Match budgets as closely as possible and report both generation samples and wall-clock/training compute; if exact matching is impossible, disclose the asymmetry.

D. **Improve preference information, not just pair count.** The 8.8% reward-variance rate means most eight-sample groups are ties. On validation, test whether more candidates per group or a different sampling temperature produces more informative same-prompt comparisons. Never create preferences from hidden labels or from a different reward.

E. **Keep RFT as the supervised control.** If resources permit, replicate the selected RFT setting across three seeds too. Do not claim GRPO is a better algorithm based on a three-seed GRPO result versus one-seed, untuned offline DPO/RFT.

## Priority 2 — test whether the learned behavior is actually memory maintenance

The current extractor GRPO gain is mostly relation-grammar validity. The central claim concerns stale facts and conflict resolution, so separate the easy structural capability from the intended capability.

For every trained arm and baseline, report:

- Downstream reader EM overall and separately for plain, alias, out-of-order, unreliable-source, relative-date, and cross-referenced-date questions.
- Extraction validity for subject, relation, value, source, and date.
- Date correctness and conflict-resolution accuracy independently of reader EM.
- Memory token count, truncation rate, and which facts were retained/dropped.
- Per-session results: whether later evidence correctly supersedes earlier facts without erasing still-valid facts.

The key v3 diagnostic is date accuracy 0.68 → 0.70 despite the large overall extractor gain. Cross-referenced-date EM is 0.57 for GRPO versus 0.74 for the 32B session-context pipeline. Do not bury this result.

## Priority 3 — test reward transfer and reader overfitting

The extractor and reward reader are both Qwen3-family models. A policy can improve on one reader's quirks without learning a generally useful memory representation.

1. Evaluate the final selected memories with at least one held-out reader from a different model family. Do not train against this reader or use its results for hyperparameter selection.
2. Keep the original frozen Qwen3-4B reader as the training reward and primary preregistered evaluator; report cross-reader results as a transfer check.
3. Inspect whether improvements survive when questions are paraphrased and when the reader receives only the compact memory, not the original stream.
4. If gains collapse on the held-out reader, describe the result as reader-specific reward optimization, not general memory improvement.

This is also the right place to distinguish reward misspecification from reward hacking. Learning relation syntax that genuinely improves the reader's answer is not, by itself, reward hacking. It is a capability shortcut relative to the intended scientific claim. It becomes a stronger reward-hacking concern if the policy exploits reader/evaluator quirks, leaks answers, or raises measured reward while the independently verified memory facts get worse.

## Priority 4 — strengthen external validity only after the above

- The current environment is MQuAKE-CF-derived, with two-session training episodes and three-to-four-session held-out episodes, entity-disjoint splits, and one frozen reader. It is a controlled testbed, not yet evidence of reliable memory in deployed frontier agents.
- After the core comparison is stable, replicate with a second generator/paraphrase seed and a fresh entity-disjoint test split.
- Then test a second task family or a real agent-memory trace set. Keep this separate from the current frozen test.
- Do not add poisoning/injection arms, PPO, reward models, or weight-space programming before the session-context result, fair DPO comparison, and held-out-reader check are complete.

## Priority 5 — produce a trace artifact, not just aggregate tables

The raw experiment outputs are currently on the original BCC machine under `/scratch/vbork001/stalestream/runs/`; they are not committed in this public repository. The current STATUS.md therefore contains aggregate evidence, not the complete per-episode trajectories.

Create a reproducible trace bundle for each arm/seed. At minimum include:

- A manifest: git commit, model IDs/revisions, dataset version and hashes, split, seed, command, hyperparameters, timestamps, GPU/software versions, and reward definition.
- Per-step training log: sampled reward, loss, gradient norm, KL if applicable, learning rate, elapsed time, and checkpoint reference.
- Per-sample generation records: exact prompt, raw completion, parsed extraction, resolved memory, token count, and parse/validation outcome.
- Reader evaluation records: episode ID, question, memory supplied, raw reader answer, exact-match result, and reward.
- For RFT/DPO: the scored candidate bank and the exact chosen/rejected pair with both reader rewards and reward gap.
- Per-seed validation/test predictions and a script that recomputes aggregate metrics and paired-bootstrap intervals.

Known run directories:
- Extractor GRPO (header context): `$S/runs/main_v3_grpo_extract/`
- Extractor round 2 (RFT/DPO bank and session-context GRPO): `$S/runs/extractor_round2/`

Because this repository is public, do not upload hidden test answer keys, hidden reliability metadata, private source code, or credentials. Keep a complete owner-accessible trace bundle in an approved private location; publish a redacted audit bundle and a manifest here. Record exact paths and checksums in STATUS.md. Do not claim the traces are available until the files have actually been exported and verified.

## Research positioning and related work

- [Beyond Final Scores: A Systematic Evaluation of Agents for Long-Horizon AI Research and Development](https://arxiv.org/abs/2608.13417) studies experience reuse that can help or mislead later decisions. This motivates memory maintenance, but also means StaleStream must identify a narrower contribution than generic experience reuse.
- [How Do Agents Fail on AutoResearch? / AutoResearchEval](https://arxiv.org/abs/2608.14905) provides 100 research tasks, 800 trajectories, and a 45-pattern failure taxonomy centered on metacognitive self-verification. This is adjacent motivation, not a substitute for our memory-specific evaluation.
- [OpenAI: How We Detect Frontier Model Misalignment](https://openai.com/index/how-we-detect-frontier-model-misalignment/) explicitly includes reward hacking, metagaming, deception, and evaluation manipulation among behaviors monitored in frontier training and agent use.

## Stop/go criteria

Continue toward a stronger paper/report only if:
1. Session-context GRPO is fully reported across three seeds.
2. A fair DPO comparison uses the same reader reward and has an on-policy or explicitly matched offline condition.
3. The gains are demonstrated on conflict/date metrics, not only relation-label validity.
4. The result transfers to a different-family reader, or the limitation is clearly stated.
5. Raw traces can be audited and aggregate metrics reproduced.

If the overall EM remains high but conflict/date metrics do not improve, reframe the result as RL improving structured extraction under downstream QA reward; do not claim that it solves stale-memory conflict resolution.
