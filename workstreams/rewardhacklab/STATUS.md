# RewardHackLab RL Agent

**Area:** RL Post-Training & Reward Design  
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11/rewardhacklab  
**Owner agent:** `rewardhacklab`  
**Current state:** ACTIVE / CONDITIONAL — corrected SFT competence gate passed; proxy-versus-verified RL comparison remains unrun

## Research aim

Measure whether state-verified RL reward improves real tool-task completion over proxy reward and supervised imitation.

## Latest completed calibration

Workflow run [43647115920](https://github.com/Vedant2100/role-work-forge-artifacts/actions/runs/43647115920) completed a corrected 210-step QLoRA SFT calibration for `CohereLabs/tiny-aya-global` (4-bit NF4, seed 2026).

The training manifest records 42 training tasks (TKT-0000–0041) and 18 disjoint evaluation tasks (TKT-0042–0059), with 210 teacher action examples.

| Measure | Base model | SFT |
|---|---:|---:|
| Independently verified successes | 0/18 | 18/18 |
| Forbidden resolutions | 0 | 0 |
| Tasks reaching finish and complete | 0/18 | 18/18 |
| Mean environment tool calls | 6 | 4 |

The preregistered RL competence gate — at least 60% held-out verified success and zero forbidden resolutions — passed. This is a supervised competence warm-start, not RL.

## Incomplete RL diagnostic

Workflow run [43641448741](https://github.com/Vedant2100/role-work-forge-artifacts/actions/runs/43641448741) was interrupted after 439.4 seconds while sampling the proxy-reward arm. The first three tasks each produced four zero-reward trajectories, so their group-relative advantages were zero and no update occurred for those groups. The run did not reach the verified-reward arm or held-out evaluation. It is not evidence for either reward hypothesis.

## Next decisive action

Use the same corrected SFT checkpoint for both reward arms. Validate nonzero reward variance and optimizer steps before the matched pilot; retain independent state verification, held-out outcomes, raw action/transition traces, multiple seeds and cost accounting. Do not alter proxy reward solely to force nonzero returns.

## Do not overclaim

SFT success is not an RL effect. Falling training loss is not sufficient evidence. The proxy-versus-verified reward comparison has not been executed.

## Evidence handoff

Compact metrics and raw evaluation records are committed under `hackathons/2026-11/results/modal-run-43647115920/` in the private source repository.
