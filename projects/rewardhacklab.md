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