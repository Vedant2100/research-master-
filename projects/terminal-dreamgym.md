# Terminal DreamGym

**Track:** Autonomous Research & Self-Improvement  
**Source:** https://github.com/Vedant2100/terminal_dreamgym  
**State:** matched evaluation executed 2026-11-12 (null primary result); skills are handwritten, not model-written  
**Decision:** HIGH if replicated

## Research question
Can failure-conditioned generated practice tasks and skill promotion yield sustained held-out/adversarial transfer beyond naive reflection?

## Existing evidence
Matched evaluation (Qwen2.5-7B, 100 tasks × 3 seeds, equal 3-attempt budget, preregistered): handwritten skills 0.572 vs no skill 0.512 strict success, +0.060 [−0.028, +0.151]; placebo 0.530; bad-advice text 0.442. The July demo (2/8,1/6,2/6 → 6/8,3/6,4/6) gave the baseline 1 attempt vs 3; the "two-seed sweep" was unit-test mock data. Details: [STATUS](../workstreams/terminal-dreamgym/STATUS.md).

## Methods / comparisons
Real model suggests patches after pytest failures; generate curriculum worlds and SKILL.md; holdout/adversarial gates; capture diffs, decisions, costs and regressions.

## Limitations and unproven claims
Skills and diagnoses are fixed handwritten text, so self-improvement is untested. Held-out tasks share repos with train tasks; weak regression check; low power (9 of 19 base tasks tie).

## Next decisive action
Model-written skills from the model's own failure traces, leave-one-family-out, same protocol; compare with handwritten, placebo and no skill.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).