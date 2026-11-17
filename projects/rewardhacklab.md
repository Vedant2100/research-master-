# RewardHackLab / Lexsi

**Track:** RL Post-Training & Reward Design  
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11/rewardhacklab  
**State:** completed SFT pilot, no RL run  
**Decision:** CONDITIONAL—fix execution first

## Research question
Does policy optimization against verified state change outperform proxy reward and supervised imitation in a tool-agent ticket workflow?

## Existing evidence
Tiny Aya Global 4-bit QLoRA trained 16 steps on 84 examples; HF adapter published; 0/6 verified successes baseline and 0/6 after; all 12 evaluations left state untouched.

## Methods / comparisons
State-verified ticket transitions, AgentTune/AuditKIT, matched pre/post tasks; compare competent base, SFT, proxy-reward RL and terminal-state RL at matched compute.

## Limitations and unproven claims
SFT NOT GRPO/RL. Decreasing loss is not useful state improvement; no proxy-vs-verified RL experiment yet.

## Next decisive action
Repair tool-call execution to get nonzero baseline, then try real RL; submit honest Lexsi Stage 1 packet by Nov 15 AoE if feasible.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).

**2026-11-16 reconciliation:** Original 0/6 SFT result is historical. Corrected shared action-history 210-step SFT yielded base 0/18, adapted 18/18 verified held-out ticket successes, zero forbidden resolutions, one seed. SFT competence gate passed, not an RL gain. Earlier GRPO pilot interrupted with no valid proxy-vs-verified reward comparison; compare both arms from same adapted checkpoint. https://github.com/Vedant2100/role-work-forge-artifacts/blob/main/hackathons/2026-11/results/modal-run-43647115920/tmp/modal-results/lexsi_tiny_aya_prompt_alignment_2026_11_14/metrics.json
