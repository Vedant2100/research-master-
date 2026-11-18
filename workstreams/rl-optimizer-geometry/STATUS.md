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
