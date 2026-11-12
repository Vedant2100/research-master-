# StaleStream RL Memory Agent

**Area:** Memory & Continual Learning
**Source:** https://github.com/Vedant2100/f26/tree/main/cs258/stalestream
**Owner agent:** `stalestream`
**Current agent state:** v0 IMPLEMENTED + EXECUTED (headroom gate FAILED vs symbolic resolver; GRPO 20-step timing measured). Next: v1 language difficulty.

## Research aim
Learn a bounded memory rewrite policy for changing facts with downstream reader reward.

## Next decisive action
Build timestamp-correct episode generator and fair symbolic/LLM baselines; measure oracle QA and GRPO runtime.

## Experimental gate
Oracle reader at least 90% EM and 20 percentage-point headroom over strongest nonprivileged baseline.

## Do not overclaim
No verified LoRA/GRPO checkpoint yet; do not leak hidden labels or overwrite unrelated coursework.

## Evidence handoff

### 2026-11-12 — v0 environment, headroom gate, GRPO timing (implemented + executed, 1 seed)
Code: `workstreams/stalestream/stalestream/` (see README). Gate script copied unchanged from `f26@1b30fd7`. Machine: 2× A30 24 GB; vllm 0.21, torch 2.11, trl 1.17, peft 0.21. Raw outputs on local `/scratch/vbork001/stalestream/runs/` (not uploaded).

**Data.** MQuAKE-CF-3k-v2, 2,764 slots; entity-disjoint split by subject hash (2,208 train / 372 test subjects). Episodes seed 2026: 2,000 two-session train, 300 three-to-four-session test. Ground truth recomputed from dates + hidden reliability; validator asserts every answer appears in the stream.

**Headroom gate v0 (300 test episodes, reader Qwen3-4B, no thinking, greedy, 160-token budget): FAIL.**

| arm | EM |
|---|---|
| oracle (privileged) | 0.999 |
| symbolic resolver (non-privileged) | 0.999 |
| newest_wins (alias-normalized) | 0.601 |
| prompted Qwen3-1.7B writer | 0.241 |
| write_all | 0.136 |
| no_memory | 0.000 |

Oracle gate passes (≥0.90). Headroom vs strongest non-privileged (symbolic) = 0.000, paired bootstrap 95% CI [−0.002, 0.002]; threshold 0.20. Cause: templated language is fully regex-parseable. Without symbolic the gap would be 0.398, but symbolic is a required baseline. Per design, add language difficulty; thresholds do not move.

**GRPO timing (20 steps, 1 seed, not a learning result).** Writer Qwen3-1.7B LoRA r=16, 4 episodes × group 8 per step, 2-session episodes, lr 1e-5, β=0, on-policy single update. Mean 22.4 s/step (rollout 5.9, reader reward 1.4, backward 15.1); 7.5 min total; no NaN; nonzero-variance groups in all steps after a seed fix. Extrapolated 300 steps ≈ 1.9 h on this config (proposal estimate 5–10 h was unverified). Reward 0.249 (first 5) → 0.273 (last 5): noise level, no learning claim.

**Not yet built:** BM25, prompted Qwen3-32B writer, consistency-check defense, privileged resolver, keep/drop controller, RFT, injections, held-out readers.

## Canonical CS258 project documents

- [Project proposal](./CS258_Project_Proposal.md) ([original DOCX](./CS258_Project_Proposal.docx); [Google Drive source](https://docs.google.com/document/d/17jOimeZCTgH-18bdfjEmTVXh46eGe8GB/edit))
- [Design document](./CS258_Design_Doc.md) ([original DOCX](./CS258_Design_Doc.docx); [Google Drive source](https://docs.google.com/document/d/1LrRCf8crBVCljb5nkpis7SB3N10L8g87/edit))

These copies capture the source documents at commit time. For subsequent edits, reconcile against the Google Drive sources before treating the snapshots as current.
