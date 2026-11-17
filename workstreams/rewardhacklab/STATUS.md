# RewardHackLab RL Agent

**Area:** RL Post-Training & Reward Design
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11
**Owner agent:** `rewardhacklab`
**Current agent state:** CONFIGURED, NOT YET DISPATCHED (no active session or actual model run assumed)

## Research aim
Measure whether state-verified RL reward improves real tool-task completion over proxy rewards.

## Next decisive action
Fix tool execution floor, reproduce 0/6 baseline, then run actual reward optimization with matched compute.

## Experimental gate
Nonzero state-completion baseline and verified before/after tool effects on heldout tasks.

## Do not overclaim
The 16-step QLoRA run is SFT not GRPO; 0/6→0/6 is not improvement.

## Evidence handoff
No master-repo independent agent handoff yet. After dispatch, include immutable source commits, commands, exact per-episode evidence, model results, matched comparisons, blockers, costs and PR links here.


**2026-11-16 reconciliation:** Corrected 210-step SFT reached 18/18 independently state-verified held-out ticket successes vs 0/18 base, zero forbidden resolutions, one seed. SFT competence gate passed. Earlier GRPO pilot interrupted after 439.4s; no proxy-vs-verified RL comparison. Next both RL reward arms from identical SFT adapter. https://github.com/Vedant2100/role-work-forge-artifacts/blob/main/hackathons/2026-11/results/modal-run-43647115920/tmp/modal-results/lexsi_tiny_aya_prompt_alignment_2026_11_14/metrics.json
