# StaleStream / CS258

**Track:** Memory & Continual Learning  
**Source:** https://github.com/Vedant2100/f26/tree/main/cs258/stalestream  
**State:** proposal and preflight, not trained  
**Decision:** HIGH—course deliverable

## Research question
Can an RL-trained bounded memory writer maintain truth across out-of-order facts, aliases, unreliable sources and revisions?

## Existing evidence
Design written, scoring/headroom checker exists. No verified trained LoRA writer or validated environment.

## Methods / comparisons
3–4 sessions, 6–10 slots, MQuAKE edits; Qwen3-1.7B LoRA writer 128–192 tokens, frozen Qwen3-4B reader; REINFORCE/controller, rejection sampling/RFT, GRPO 8/group; 3 seeds if feasible.

## Limitations and unproven claims
Must compute true state from timestamps not delivery order; no hidden-label exposure; memory update ≠ general recursive learning. Reader transfer and injection robustness unproven.

## Next decisive action
Nov 12 proposal target; Nov 19 300 held-out episodes with oracle QA >=90% and >=20 point gap vs strongest fair baseline plus measured 20-step timing; Nov 24 GRPO pilot; Dec 3 freeze; Dec 10 report.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).