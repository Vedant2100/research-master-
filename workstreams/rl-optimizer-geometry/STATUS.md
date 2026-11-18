# RL Optimizer Geometry — Status

**Stage:** DESIGNED / SOURCE IMPORTED / CPU DIAGNOSTIC CODE ADDED. No real RL experiment run or result verified. No automated agent session or paper submission.
**Track:** RL Post-Training & Reward Design
**Issue:** https://github.com/Vedant2100/research-master-/issues/22

## Evidence
1. Author's exact MIT code is stored in vendor/vukrosic/ at upstream commit d0dc052749a97061f6daa6907371bd0a2ec33405. This is attribution, not an original scientific result.
2. Author ss.py reads FineWeb binary slices not contained in the public paper directory and hardcodes a single torch seed (0); no faithful reproduction is claimed.
3. Official Pion RL/verl has a shared trainer containing AdamW, Muon and Pion; pinned SHA 87965014b360bde604632cba0aa12e423c6c63c6. x66ccff/verl-muon has ALFWorld integration; pinned SHA 6692817d594d45af8558f719261edde14fcb63b2.
4. Offline gradient diagnostic and CPU tests are included. These do not verify any optimizer comparison.

## Next decisive actions
- Run independent CPU source theory_check and local diagnostic tests, recording dependencies and output.
- Audit full GPU/VRAM feasibility, task competence and unsaturated headroom, licensing and FSDP parameter routing. Official two-GPU recipes do not guarantee fit on available GPUs.
- Freeze tasks, model, verifier, splits, 3 independent training seeds, LR grids, reward noise, advantage estimator, clipping/KL, applied-update RMS and exact model/trainer SHAs.
- Obtain explicit cost cap and GPU approval. Only then run one cheap competence/control pilot; scale only if it reveals real optimizer-sensitive effects.

**Stop/no-go:** if fair tuning or matching applied-update RMS removes differences; no held-out predictive diagnostic; poor competence; excessive cost. Negative results must be reported.
**Handoff:** use repository templates/EXPERIMENT_HANDOFF.md and do not claim run success from code or CI checks alone.

## CPU-only verification (2026-11-17)
- On a local, equivalent copy of the committed diagnostic and tests, Python unittest reported **4 tests passed** with NumPy 2.3.5; a synthetic identity-gradient NPZ produced split-half cosine 1.0, stable rank 4.0, tail-energy fraction 0.5. This verifies arithmetic only, not policy-gradient measurement.
- The author's standalone theory_check.py was run with NumPy 2.3.5: momentum cosines 0.8997/0.9499/0.9899 for μ=0.9/0.95/0.99; finite-difference and analytic derivative both 0.568103. This is original source's toy check, not an independently reproduced optimizer-training result.
- Source audit verified exact Git blob SHA identity for vendored ss.py, drive.py, theory_check.py and LICENSE against the pinned author commit.

## Updated novelty/readiness gate — 2026-11-17

- **Scientific readiness:** suitable for Phase 0 diagnostic engineering; **not yet** an original, defensible optimizer contribution or a fair RL training comparison.
- **New overlap discovered:** Ares (Oct 12, 2026) already performs RLVR gradient spectral tracking and adaptive-rank updates; Chen et al. (Oct 22) studies structured gradient-noise effects on Muon; Khalil & Hoque (Nov 9) analyzes post-training rank and update alignment. Added to LITERATURE.md, with an updated prospective counterfactual/independent-rollout test in RESEARCH_PLAN.md.
- **Existing diagnostic is insufficient by itself:** two split gradients, stable rank and cosine alone do not demonstrate a predictive signal. Next code work must add disjoint-group gradient capture, principal-angle/projector overlap and a held-out third-split target, followed by calibrated controls. Do not claim novelty or training success.
- **Compute gate unchanged:** full-model RLVR, Ares/Pion integration and GPU budget/hardware feasibility are not verified. No new GPU job is authorized by this status update.
## Trainer preflight, CPU only (2026-11-17)
Code: `modal/cost_probe.py` (`--mode preflight`, CPU container, official image `verlai/verl@sha256:9576682f…` = vLLM 0.12.0, torch 2.9.0, flash-attn 2.8.1; Pion fork at 87965014 installed editable). **12/12 checks pass.** No GPU step has run.

Findings that would have broken a GPU run:
1. **Pion fork cannot compose its own recipes.** Pion's root `.gitignore` has `**/data/`, which dropped `RL/verl/verl/trainer/config/data/legacy_data.yaml`; `ppo_trainer.yaml` fails with `MissingConfigException: Could not find 'data/legacy_data'`. Upstream verl's current file has drifted from the fork, so the probe rebuilds it from the fork's own `_generated_ppo_trainer.yaml` `data:` block; the composed default config is then identical to that generated reference (only the Hydra selector `model_engine` differs, by design).
2. **Fork README install is stale.** It says torch 2.6 and leaves vLLM unpinned, but the code imports vLLM ≥0.11 APIs (`vllm.utils.argparse_utils`, `vllm.config.lora`); verl 0.7 moved to vLLM 0.12.0. We use the official vLLM 0.12 verl image instead.

Verified on CPU: all trainer, FSDP-worker, vLLM async rollout and muon imports; GSM8K 7473/1319 rows (7 steps/epoch → 105 steps for the 15-epoch recipe); Qwen3-1.7B (16 Q / 8 KV heads, tied embeddings), max prompt 235 tokens < 512; GSM8K reward 1/0/0 on correct/wrong/missing; AdamW, MuonAdamW and DefaultPionAdamW recipes compose and pass verl `validate_config`; one optimizer step on a tiny Qwen3 for each, with Muon/Pion routing all 14 projection matrices to Muon and embeddings + norms to AdamW. All three recipes use the same lr=1e-6, which is not a fair-tuning control (see RESEARCH_PLAN item 3).

Not verifiable on CPU: FSDP2 + vLLM sleep/wake on GPU, Muon/Pion on DTensor shards, real memory fit. Those are the GPU probe's job (3 Muon steps, timing only).

Budget: Modal CPU preflights only, < $1. Modal GPU was blocked at the time (no payment method; since fixed), and the owner chose the free cluster anyway (RTX 6000 Ada 48 GB, same AD102 chip as Modal L40S).

## GPU timing probe on the cluster (2026-11-18)
Scripts: `cluster/setup.sh`, `cluster/probe.sbatch` (same pinned image as the Modal preflight, run with Apptainer). Official Muon recipe, unchanged except no wandb, no checkpoints, no validation, and the model loaded from the local snapshot. Cost: $0.

| Hardware | Batch | Steps | s/step (gen / logprob+ref / update) | Peak alloc | Reward (critic/score/mean) per step |
|---|---|---|---|---|---|
| 2× RTX 3090 24 GB (job 314560) | 32 prompts (smoke) | 3 | ~75 | 15.9 GB | 0.00 → 0.02 |
| 2× RTX 3090 24 GB (job 314565) | 1024 prompts (official; micro-batches 4/8 to fit) | 2 | 2425, 2348 (~880 / ~480 / ~1020) | 16.4 GB | 0.002, 0.02 |
| 2× RTX 6000 Ada 48 GB (job 314561) | 1024 prompts (official recipe exactly) | 3 | 1273, 1232, 1170 (~490 / ~245 / ~480) | 34.2 GB | 0.003, 0.013, 0.246 |

- FSDP2 + vLLM sleep/wake and MuonAdamW on DTensor shards run end to end. All runs log a `DataLoader worker ... Killed` traceback at shutdown, after the last step has been written; the job still exits COMPLETED.
- **Projected cost of a full 105-step run:** about 20 min/step on Ada, so ~36 h per run including validation. On Modal 2×L40S (same chip) that is ~$140 per run, ~$420 for the 3-optimizer pilot. Too expensive, so the pilot runs on the cluster: ~36 h per run on Ada, ~72 h on 3090s.
- **Format-learning confound:** 47–59% of responses hit the 1024-token limit (Qwen3 thinking), and the strict GSM8K reward needs `#### N`, so the starting reward is ~0. Reward rose to 0.25 by step 3. Early curves mostly measure format learning, and optimizer differences there are not evidence of a geometry effect. Compare plateau and held-out val accuracy, not early slope.
- Bugs fixed on the way: `/scratch` is node-local on this cluster (everything now under `~/rog` on NFS); transformers 4.57.3 calls the Hub API for a model id even with `HF_HUB_OFFLINE=1` (load from the local snapshot path); verl rejects a model path with a trailing `/`.

## Go/no-go pilot: cancelled (2026-11-18)
`cluster/pilot.sbatch` was set up to run the official 105-step recipe for AdamW, Muon and Pion, 1 seed each, one at a time on 2 Ada GPUs, with `data.seed=1` so all three see the same data order. The owner cancelled it before it started (jobs 314871-314873) because it would take too long: ~36 h per run, ~4.5 days of serial GPU time plus queue waits. No optimizer comparison was run, so the workstream has no evidence for or against an optimizer-geometry effect in GRPO.

What exists for anyone who picks this up:
- Working cluster pipeline (`cluster/`), with the recipe verified end to end for Muon only. AdamW and Pion recipes have passed the CPU preflight but have never run on a GPU.
- Raw per-step metrics of the three probe runs in `results/cluster_probe/` (verl FileLogger JSONL).
- Cheaper options if revisited: fewer steps (e.g. 30-40 steps, past the format-learning phase), a smaller batch, or a smaller model. Each departs from the official recipe and would need to be reported as such.
