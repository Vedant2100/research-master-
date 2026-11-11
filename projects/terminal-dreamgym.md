# Terminal DreamGym

**Track:** Autonomous Research & Self-Improvement  
**Source:** https://github.com/Vedant2100/terminal_dreamgym  
**State:** implemented live loop, conflicting result protocols  
**Decision:** HIGH if replicated

## Research question
Can failure-conditioned generated practice tasks and skill promotion yield sustained held-out/adversarial transfer beyond naive reflection?

## Existing evidence
Live Qwen2.5-7B demo baseline train/heldout/adv 2/8,1/6,2/6; reflection 4/8,2/6,1/6; gated 6/8,3/6,4/6. Later two-seed sweep reports zero deltas and 100% false promotion under its metric.

## Methods / comparisons
Real model suggests patches after pytest failures; generate curriculum worlds and SKILL.md; holdout/adversarial gates; capture diffs, decisions, costs and regressions.

## Limitations and unproven claims
Single positive demo and null sweep are not same protocol; cannot claim robust self-improvement. Mock runs not evidence of model learning.

## Next decisive action
Reconcile test splits/prompts/protocol and repeat matched multiple seeds; compare no-skill, reflection, naive gate, heldout gate; then prepare genuine demo/paper.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).