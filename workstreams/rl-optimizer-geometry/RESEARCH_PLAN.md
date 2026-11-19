# Research Design and Precommit Protocol — 2026-11-17

**Title (working):** When Does Gradient Geometry Help Reinforcement Post-Training?

## Specific gap
Muon can work well for some sparse-reward agentic RL configurations (Ruan et al. 2026) but fail in some RLVR regimes (Fan et al. 2026); different models/objectives, update magnitudes and engineering choices confound comparison. Pion, MuonMax/Momo, ISO and GRPO rank analysis are already in literature. A new contribution would be a **prospective, held-out diagnostic** and controlled mechanism linking reward/gradient quality to optimizer behavior—not rediscovering the existing optimizers.

## Falsifiable hypotheses
- **H1:** Gradient split-half coherence and matrix spectral concentration from independently sampled trajectories at identical frozen policy weights predict later optimizer degradation, above and beyond model, task, gradient clipping, KL and applied update RMS. Null: no held-out predictive information.
- **H2:** In low-coherence regimes, Pion outperforms Muon at matched budgets and fair separately tuned learning rates. A *separate* update-RMS-matched control tests whether the effect is actually spectral geometry or effective step size. Null: no advantage after these controls.
- **H3 (optional):** Rosić's early-adapt-then-hold hypergradient Muon controller can reduce LR sweep cost in RL without sacrificing verified task reward. This method is prior work; if results are only scheduler engineering, do not claim novelty.

## Existing implementation, no second harness
**Primary:** use official Pion RL/verl pinned 87965014b360bde604632cba0aa12e423c6c63c6, with GRPO and a common AdamW/Muon/Pion trainer. Candidate tests: Qwen3-1.7B, GSM8K and MATH 3–5, **only after** memory/compute preflight. Primary publication-grade comparisons must be within one frozen trainer.

**Secondary transfer:** x66ccff/verl-muon pinned 6692817d594d45af8558f719261edde14fcb63b2, ALFWorld Qwen2.5-0.5B. Do not pool metrics between different framework/model/task settings as if matched. FSDP NO_SHARD may exceed VRAM.

**Reference only:** original MIT Rosić tiny LM ss.py, drive.py, theory_check.py pinned d0dc052749a97061f6daa6907371bd0a2ec33405; no official training data included. The code does not run GRPO.

## Pre-registration and fairness requirements
1. Before comparing optimizers, establish a competent, non-ceiling, valid verifier baseline and held-out task partition; log actual task success and reward failures (not only loss).
2. Freeze model/checkpoint SHA, dataset/verifier version, train/validation/test IDs, trainer/runtime SHA, precision, optimizer parameter routing (matrix vs embeddings/norms/head), GRPO advantage normalization, group size, clipping, KL, number of sampled rollouts, max tokens and hardware. Do not leak test tasks into LR selection.
3. Prebudget each optimizer's LR/schedule sweep fairly. Compare **matched sampled tasks and total steps/tokens** and independently report **matched actual applied update RMS** with same optimizer inclusion set. Numerical LR equality across AdamW/Muon/Pion is NOT a fair control.
4. At fixed policy checkpoints, save independent half-batch gradient aggregates from non-overlapping trajectories and calculate per-matrix pre/post clip split-half cosine, stable rank, spectral tail energy. Pairs must be genuinely independent for noise interpretation; a correlation is not an SNR calibration. Include attention Q/K/V and MLP shapes separately.
5. Compare AdamW, Muon (whole/per-head as appropriate), Pion (whole/per-head as appropriate), and optionally hypergradient-controlled Muon. Separate reward-noise intervention from optimization intervention, and contrast reward corruption with clean verifiers.
6. Primary end points: held-out verified task success and time/sample efficiency. Also record reward progression, entropy, KL, clipping frequency, divergence, token use, wall time/GPU hours, update RMS, rank, predicted-vs-observed outcomes and failure denominators.
7. **Confirmation:** at least 3 independent training seeds (not merely deterministic replay seeds), CIs, fixed budget and a held-out task family where any predictive threshold is frozen before evaluation. A retrospective fit is hypothesis generation only.

## Phase gates
**Phase 0 — no GPU:** inspect source licenses, sanity-check borrowed code and our diagnostics, check that paired gradients can actually be collected at identical weights and without task leakage.
**Phase 1 — feasibility / explicit approval needed:** verify single-model VRAM fit for FSDP2 + vLLM + optimizer on available GPU resources; record estimated dollars/GPU-hours; 1 baseline competency pilot.
**Phase 2 — authorized pilot:** matched AdamW/Muon/Pion controls on one task, with measured updates and independent gradient samples.
**Phase 3 — replication/transfer:** >=3 seeds, held-out task distribution, prospective prediction; test optional early-adapt scheduler only if it is relevant.
**Phase 4 — new method (conditional):** propose a gradient-quality-conditioned spectral update only if it beats tuned controls prospectively and reproducibly.

**Go/no-go suggestion, not achieved:** proceed to replication if baseline is competent and at least 5 percentage points of verified success or a reproducible collapse/stability contrast remains after fair controls. Stop for inadequate competence, saturation, invalid reward, no predictive gradient feature, or expenses outside approved cap. Even a negative outcome can support a rigorous study, but no paper claim yet.

## Risks and disclosures
Muon modifies spectral geometry and update magnitude together. GRPO gradients can be sparse/low rank for reasons unrelated to the optimizer, and reward noise is distinct from gradient stochasticity. Split-half cosine from two half-batches is only a proxy. SFT loss is not verified RL success. Two GPUs in a public recipe do not guarantee fit on any particular A30 allocation. No GPU run or external paper submission is authorized by this plan.

## Novelty gate / revised decisive experiment — 2026-11-17

**Status: NOT YET NOVEL.** New October/November prior art (see LITERATURE.md) includes Ares (spectral adaptive rank in RLVR), structured-noise Muon theory, and RLVR rank/step-direction studies. Treat the original broad H1/H2 above as exploratory, **not as paper claims**.

### Sharper scientific question
When two or more independent on-policy rollout groups are sampled at an **identical frozen policy state**, are the *reproducible gradient directions* better predictors of downstream **held-out verified reward response to candidate optimizer steps** than the energy spectrum alone? Can optimizer failures be attributed to amplification of *unreproducible* directions rather than to effective step size, advantage estimator, task mix, or KL/clipping?

This is a **hypothesis**, not a demonstration of novelty. Related split-batch subspace reproducibility work in low-rank pretraining must be cited and separated carefully.

### Stage A — counterfactual directional diagnosis, without full training
1. At multiple independently sampled, **fixed policy checkpoints**, generate at least three disjoint on-policy rollout/gradient groups for each selected task difficulty and reward/noise regime. Compute per-matrix gradients **before optimizer transformations**, controlling reward baseline, group size and advantage estimator. Prefer independent prompt groups or account for within-prompt correlation.
2. For a selected matrix, compare (i) gradient spectral energy/effective rank (Ares), (ii) split-half gradient cosine, (iii) top-k **projector overlap / principal angles** across disjoint groups and (iv) cost-normalized update direction projected on the third **held-out** gradient group. Calibrate estimator repeatability using synthetic known-signal/noise positive and negative controls. Distinguish real gradient from checkpoint displacement.
3. Generate **counterfactual single steps** with cloned identical weights **and optimizer states** for AdamW, Muon, Pion, and Ares where implementable. Control applied-update norms, comparable parameter routing, and KL trust-region displacement; evaluate next-step held-out policy surrogate plus a separate sampled **verified reward** estimate with uncertainty. A surrogate improvement is not assumed to improve environment reward.
4. Use fixed, preregistered predictors/thresholds based only on training/validation checkpoints to predict a ranking or failure regime on a held-out task family/checkpoint. Compare against always-AdamW, always-Pion, update-RMS only, LR/clip/KL metrics, gradient norm, spectral effective rank and a simple task-difficulty/advantage predictor.
5. If predictors do not beat these cheap baselines on out-of-distribution conditions, publish a negative diagnostic if rigorous or stop. If they do, run a **separate**, matched-budget multi-seed prospective intervention. No optimizer proposal before this.

### Stage B — training confirmation (explicit compute approval required)
- Use a **single fixed RL framework** and fair tuned AdamW, Muon, Pion and (if proposing spectral filtering) Ares. Three truly independent training seeds per key comparison; no test-set tuning; record task success, reward AUC, variance, wall-time/GPU-hours, KL, update RMS, clipping and failure denominator.
- Test both clean and controlled noisy rewards, and at least two difficulty/advantage regimes. Transfer prediction to held-out task families and optimizer settings.
- Separate **scientific utility** (reward at equal tokens/rollouts) from **systems cost** (additional backwards, SVDs, synchronization, optimizer-state copies). Two extra backward passes every step may erase any practical gain. A predictor must show *net* value or run only periodically.
- Mark the hypothesis **falsified** if projectors are not repeatable, prediction fails out of distribution, differences disappear after tuned LR/update-RMS controls, or diagnostic overhead exceeds the savings.

### Concrete acceptance criteria (proposals, not observed)
A nontrivial mechanism requires: (i) reproducible independent-gradient statistic, (ii) prospectively held-out predictive gain over effective-rank and strong cheap controls, (iii) matched-step causal support beyond update magnitude and objective, and (iv) replicated verified-reward outcome. A paper submission must explicitly differentiate Ares, Pion and structured-noise Muon analysis. A new optimizer needs a demonstrably novel update rule, not just a renamed spectral filter.

**Current hardware/run readiness:** CPU source and arithmetic checks are not a model-competence pilot; the Pion FSDP2/vLLM GPU fit, checkpoint availability, reliable reward harness, per-step gradient capture, cost budget and three-seed run plan remain unverified. **Do not start expensive training yet.**

