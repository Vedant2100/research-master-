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

### 2026-11-12 — v1 preregistration (written before the v1 run)
- **Change:** language difficulty only. Episodes regenerated with seed 2027 and mixed absolute date surface forms (ISO, `March 5, 2023`, `5 March 2023`, `Mar. 5, 2023`, `2023/03/05`); every stream line paraphrased by Qwen3-4B (temperature 0.9, 3 tries) with verbatim preservation of source, date string, subject/alias and value, audit lines must still negate, ordinary lines must not, and no other episode value may leak. Failed lines fall back to the template; fallback rate is reported. Structure (slots, timelines, unreliable source, audit, questions, splits) unchanged from v0.
- **Hypothesis:** paraphrase breaks the template-regex symbolic resolver while the oracle stays ≥ 0.90, giving headroom ≥ 0.20 vs the strongest non-privileged baseline.
- **Controls/arms:** oracle (privileged), no_memory, write_all, newest_wins, symbolic (same v0 grammar + multi-format date parser; control: 1.000 answer-in-memory on unparaphrased v1), prompted Qwen3-1.7B writer. Reader, prompt, budget (160 tokens) and thresholds unchanged from v0.
- **Split/seeds:** 300 test episodes, entity-disjoint, 1 generator seed (2027), 1 paraphrase seed (7), greedy reader.
- **Known limitation:** paraphraser and reader are the same model (Qwen3-4B); the symbolic resolver is not re-engineered for paraphrase, so a pass shows headroom over *this* resolver, and a stronger rule system could narrow it. Thresholds do not move.
- **Budget:** local 2× A30 only, est. < 1 GPU-hour.

### 2026-11-12 — v1 result: headroom gate PASS (1 seed, 300 test episodes)
Paraphrase: 7,842 test lines, 7,268 paraphrased, **fallback 7.3%** (template lines remain). All 300 episodes pass the label validator.

| arm | v0 EM | v1 EM |
|---|---|---|
| oracle (privileged) | 0.999 | 0.999 |
| prompted Qwen3-4B writer (added post-prereg as a stricter check) | 0.269 | 0.223 |
| prompted Qwen3-1.7B writer | 0.241 | 0.222 |
| write_all | 0.136 | 0.142 |
| symbolic resolver | 0.999 | 0.078 |
| newest_wins | 0.601 | 0.077 |
| no_memory | 0.000 | 0.000 |

Gate (all non-privileged arms incl. prompted_4b): strongest = prompted_4b, oracle − strongest = **0.776**, paired bootstrap 95% CI [0.758, 0.795] → **PASS** (oracle ≥ 0.90, headroom ≥ 0.20).

**Caveats (do not overclaim):** (1) the required prompted **Qwen3-32B** writer is not yet run; it is the most likely baseline to narrow the gap. (2) The symbolic resolver was not re-engineered for paraphrase; its collapse shows that template rules no longer suffice, not that no rule system could. (3) Paraphraser = reader model (Qwen3-4B). (4) One generator seed, one paraphrase seed. (5) Prompted writers score low partly because they garble dates and overrun the 160-token budget, so the headroom is partly format competence, which RL may learn without learning conflict resolution; memory-correctness metrics by difficulty tag are needed to tell these apart.

### 2026-11-12 — v1 GRPO/RLOO pilot preregistration (written before the run)
- **Runs:** GRPO (std-normalized group advantage) and RLOO (leave-one-out), 100 steps each, same everything else: Qwen3-1.7B LoRA r=16 α=32, lr 1e-5, 4 episodes × group 8 per step (3,200 trajectories per run), 2-session v1 train episodes, temperature 1.0, β=0, one on-policy update per batch, reward = Qwen3-4B reader EM, seed 0. Matched sampling budget by construction.
- **Eval:** greedy writer with final adapter on the 300 v1 test episodes (3–4 sessions, held-out entities); same reader; compared paired to prompted_1.7b (0.222, the same model without training).
- **Learning-signal criterion (decides the Nov 24 branch):** trained − prompted_1.7b on test EM with paired bootstrap 95% CI excluding 0, for at least one of GRPO/RLOO. Otherwise: "no learning signal at 100 steps" and RFT becomes the main trained writer per the design. Train-reward trend (mean of last 20 vs first 20 steps) reported but not decisive.
- **Not tested here:** seeds, held-out readers, RFT, controller. One seed only: no claim about GRPO vs RLOO ranking.

**Not yet built:** BM25, prompted Qwen3-32B writer, consistency-check defense, privileged resolver, keep/drop controller, RFT, injections, held-out readers.

## Canonical CS258 project documents

- [Project proposal](./CS258_Project_Proposal.md) ([original DOCX](./CS258_Project_Proposal.docx); [Google Drive source](https://docs.google.com/document/d/17jOimeZCTgH-18bdfjEmTVXh46eGe8GB/edit))
- [Design document](./CS258_Design_Doc.md) ([original DOCX](./CS258_Design_Doc.docx); [Google Drive source](https://docs.google.com/document/d/1LrRCf8crBVCljb5nkpis7SB3N10L8g87/edit))

These copies capture the source documents at commit time. For subsequent edits, reconcile against the Google Drive sources before treating the snapshots as current.
