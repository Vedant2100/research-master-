# RewardHackLab / Lexsi

**Track:** RL Post-Training & Reward Design  
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11/rewardhacklab  
**State:** corrected SFT competence calibration complete; actual RL comparison not run  
**Decision:** ACTIVE / CONDITIONAL — proceed to a small matched RL pilot only

## Research question

Does policy optimization against independently verified state changes outperform proxy reward and supervised imitation in a tool-agent ticket workflow?

## Latest verified evidence

Workflow run [43647115920](https://github.com/Vedant2100/role-work-forge-artifacts/actions/runs/43647115920) completed the corrected 210-step QLoRA SFT calibration for `CohereLabs/tiny-aya-global` (4-bit NF4, seed 2026). The 42 training tasks (210 teacher actions) and 18 evaluation tasks are disjoint: TKT-0000–0041 for training, TKT-0042–0059 for evaluation.

- Base model: **0/18** independently verified successes; zero forbidden resolutions. It repeatedly called `lookup_policy` and never reached `finish` or `complete`.
- SFT model: **18/18** verified successes; zero forbidden resolutions; all five action stages completed.
- The preregistered competence gate (at least 60% held-out verified success and zero forbidden resolutions) passed.

This is a supervised competence warm-start, **not GRPO or RL**.

## Incomplete RL attempt

The earlier GRPO-style pilot [43641448741](https://github.com/Vedant2100/role-work-forge-artifacts/actions/runs/43641448741) was interrupted after 439.4 seconds while sampling the proxy arm. The first three training tasks each produced four zero-reward trajectories, so those groups had zero relative advantages and no policy update. The run never reached the verified-reward arm or held-out evaluation. It is an incomplete diagnostic, not a result.

## Next decisive action

Use the same corrected SFT checkpoint for both arms. First validate nonzero reward variance and optimizer updates, then run a small matched proxy-reward versus independently verified terminal-state reward comparison. Preserve held-out evaluation, multiple seeds, action/transition traces and cost accounting. Do not tune the proxy reward merely to force nonzero returns.

## Limitations

The 18-task calibration is a competence gate, not evidence that either reward objective improves the policy. No proxy-versus-verified RL effect has been measured, and no RL claim should be made until the paired experiment and held-out evaluation exist.
