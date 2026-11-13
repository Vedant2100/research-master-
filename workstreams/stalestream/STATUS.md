# StaleStream RL Memory Agent

**Area:** Memory & Continual Learning
**Source:** https://github.com/Vedant2100/f26/tree/main/cs258/stalestream
**Owner agent:** `stalestream`
**Current agent state:** gate v3 MARGINAL PASS (oracle 0.997 vs 32B session-context extraction+rules 0.783, gap 0.214, 95% CI [0.194, 0.234]). v2 failed the 32B check. Run 1+2 (seed 0): GRPO +0.109 test EM over the untrained writer (gains on conflict slots); RFT, DPO and frozen-teacher OPSD ≈ untrained. Next: hinted-teacher diagnostic, small RFT/DPO tuning on val, GRPO seeds 1–2. Full fine-tuning GRPO implemented and timed (21.4 s/step). Next: RFT/DPO sample bank, then main runs (HANDOFF section B).

## Research aim
Learn a bounded memory rewrite policy for changing facts with downstream reader reward.

## Next decisive action
See `HANDOFF.md`. Gate v2 failed the 32B-extractor check: redesign conflicts so rules over perfect extraction cannot solve them (HANDOFF A6b), regenerate (v3), rerun the gate, then train.

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

### 2026-11-12 — v1 pilot result (1 seed; executed, not replicated)
Training: 100 steps each, 22.6 s/step, ~38 min per run. GRPO train reward by 20-step block 0.241 → 0.251 → 0.244 → 0.265 → 0.283; RLOO ended at a similar level (RLOO grad norms ~5× smaller than GRPO at the same lr, since its advantages are not std-normalized — a confound in any GRPO-vs-RLOO reading).

Held-out v1 test (300 episodes, paired bootstrap vs the same model untrained, prompted_1.7b = 0.222):

| arm | EM | Δ vs prompted_1.7b [95% CI] |
|---|---|---|
| grpo_100 | 0.252 | +0.030 [+0.007, +0.054] |
| rloo_100 | 0.251 | +0.029 [+0.003, +0.054] |
| grpo − rloo | | +0.001 [−0.021, +0.024] |

Preregistered learning-signal criterion: **met** (both CIs exclude 0). **But** the gain is concentrated in slots with no conflict feature ("plain": 0.298 → 0.387 GRPO) and comes with shorter memories (149 → 119 tokens); unreliable-source (0.214 → 0.225 / 0.208) and out-of-order (0.218 → 0.235 / 0.222) slots barely move. Interpretation: 100 steps of RL mostly learned format/budget compliance, not conflict resolution. No GRPO-vs-RLOO claim.

**Open validity issue (blocks extensive training):** the v1 gate passed only against a template-regex resolver. The missing strong non-privileged baseline is *LLM extraction + symbolic resolution* (an LLM turns each paraphrased line into (subject, relation, value, date, source) tuples; rules then do aliasing, dates and audit-based source exclusion). If it nears the oracle, RL's remaining advantage is small and mostly about parsing; the environment then needs reasoning that this pipeline cannot do, before more RL. Next: build and run this baseline (pilot), then decide.

### 2026-11-12 — audit before gate v2
`scripts/audit.py` (data invariants on 12,600 episodes across v0/v1_raw/v1; recomputation of every number above): **0 failures**; all recorded numbers reproduce. Manual check of 20 random v1 paraphrases: all faithful, but light rewrites close to the templates (an LLM extractor will likely recover most facts). Issues found: (1) no validation split exists; the gate and the pilot both used the v1 test set, so the v1 pilot is **exploratory** and gate v2 needs a fresh frozen test set; (2) paraphrase faithfulness is only spot-checked; (3) RLOO mean grad norm 0.054 vs GRPO 0.336 at equal lr; (4) vLLM sampling is not bit-reproducible.

### 2026-11-12 — gate v2 preregistration (written before the gate v2 run)
- **Why v2:** v1 gate passed only against template baselines; budget did not bind (oracle ~99/160 tokens); questions were not conflict-focused; no validation split; v1 test already used by the pilot.
- **Environment v2:** seed 2028, mixed dates, **8–12 facts/episode** (oracle full-sentence memory mean 125, p90 150 tokens, budget 160), **conflict-focused questions** (asked slots must carry an alias / unreliable / out-of-order feature when available; 97% on a 200-episode draw), same paraphrase recipe as v1 (Qwen3-4B, seed 7). **3-way entity-disjoint split** (train/val/test = 1,728/346/346 subjects; test hash buckets identical to v1), with the 160 subjects in FactConsolidation-6K excluded from all splits. 2,000 train (2-session), 300 val, 300 test (3–4 sessions).
- **Arms (all non-trained, all evaluated on val and on the frozen test set):** oracle (privileged), no_memory, write_all, newest_wins, symbolic (template regex), **bm25** (top-2 statements per question; sees questions and raw history), **extract_rules** (Qwen3-4B per-line JSON extraction with the public relation list + the same rules as symbolic), prompted writers **Qwen3-1.7B, Qwen3-4B, Qwen3-32B-AWQ**. Reader Qwen3-4B, budget 160, unchanged.
- **Gate (thresholds unchanged):** on test, oracle ≥ 0.90 and oracle − strongest non-privileged arm ≥ 0.20, paired bootstrap. If extract_rules or the 32B writer is within 0.20 of the oracle, the gate FAILS and conflicts are redesigned before any training.
- **Paraphrase faithfulness:** Qwen3-32B-AWQ judges 400 random paraphrased test lines; > 2% unfaithful (point estimate) → regenerate before using the data.
- **Known limitations:** extraction uses the same model family as the reader and paraphraser; BM25 is question-aware by design; one generator and one paraphrase seed.

### 2026-11-12 — hinted-teacher diagnostic: the OPSD teacher is no better than the student
`writer.py --teacher-hints` (the OPSD teacher prompt: resolved dates, aliases so far, unreliable source after its audit) on v3 **val**: Qwen3-1.7B **0.196** (vs 0.194 without hints), Qwen3-4B **0.177** (vs 0.194). The prompted models do not use the hints. Their bottleneck is compressing and prioritizing within 160 tokens, not missing information. So the frozen-teacher OPSD null is explained: **there was no better teacher to distill from**, and the null is uninformative about distillation as a method. A meaningful OPSD needs a teacher that is actually better, e.g. a hinted teacher given an example of the target format, a larger hinted teacher (on-policy distillation from a stronger model), or the GRPO-trained writer as teacher. Each must be checked on val *before* distilling.

### 2026-11-12 — main run 2 results (seed 0): only GRPO improves over the untrained writer
| arm (seed 0, final ckpt) | val EM | test EM | Δ test vs prompted_1.7b [95% CI] | GRPO − arm (test) |
|---|---|---|---|---|
| prompted_1.7b (untrained) | 0.194 | 0.211 | — | +0.109 [+0.082, +0.137] |
| RFT (best-of-8 SFT, 2 ep, lr 5e-6) | 0.212 | 0.211 | −0.001 [−0.023, +0.023] | +0.109 [+0.085, +0.136] |
| DPO (559 pairs, β 0.1, lr 1e-6, 1 ep) | 0.210 | 0.223 | +0.012 [−0.008, +0.032] | +0.097 [+0.069, +0.126] |
| OPSD, frozen teacher, derivable hints (300 steps) | 0.211 | 0.206 | −0.006 [−0.028, +0.018] | +0.114 [+0.088, +0.141] |
| **GRPO (300 steps)** | **0.327** | **0.320** | **+0.109 [+0.082, +0.137]** | — |

Per-tag (test): only GRPO moves the conflict tags (out_of_order 0.21 → 0.40, xref_date 0.20 → 0.32, relative_date 0.19 → 0.32, unreliable 0.19 → 0.27, alias 0.21 → 0.30); RFT, DPO and OPSD stay within ±0.04 of the untrained writer on every tag. Memory length is unchanged across arms (153–159 tokens).

**Training notes.** OPSD-frozen was stable for 300 steps (no collapse guard; reward 0.19–0.23 throughout; KL 0.30 → ~0.21–0.25), so the frozen teacher fixed the collapse, but distilling toward the hinted teacher did not raise QA. RFT reached SFT loss 0.04 (98.8% token accuracy on its own samples). DPO loss moved only 0.69 → 0.66 in 35 steps (weak update).

**Caveats, do not overclaim:** one seed per arm. RFT and DPO used one conservative hyperparameter setting each, untuned. The DPO update was very small, so "DPO does not help" is not established. Untested diagnostic for OPSD: whether the *hinted teacher itself* writes better memories than the student. If it does not, OPSD has no signal to distill and its null is uninformative about distillation.

### 2026-11-12 — main run 2 preregistration (written before the run)
- **Frozen-teacher OPSD smoke test (10 steps):** teacher = frozen initial writer in-process on GPU 0 (bf16), paged 8-bit AdamW to make room; peak 21.1 GB, ~35 s/step, KL loss 0.27–0.33 (no drift to 0), reward 0.15–0.23, 205–227 tokens. A three-server variant (teacher on GPU 1) failed: the writer's 1 GB weight-transfer buffer did not fit on GPU 1 (OOM → 500 → trainer hang).
- **Sample bank (`bank.py`, base writer, 600 v3 train episodes × 2 shared states × 8 = 9,600 samples):** mean reward 0.213; 1,098 RFT examples (mean reward 0.378), 559 DPO pairs (mean gap 0.416).
- **Runs (seed 0, full fine-tuning, final checkpoint, no selection):** RFT (SFT on best-of-group, lr 5e-6, 2 epochs), DPO (β 0.1, lr 1e-6, 1 epoch, precomputed reference), OPSD-frozen (300 steps, 32 episodes × 1, derivable hints, full-vocab reverse KL to the frozen teacher; collapse guard stops it if 10 steps sit at the length cap with reward < 0.05). `scripts/main_v3_run2.sh`.
- **Criteria:** as in run 1: Δ vs prompted_1.7b with paired bootstrap CI excluding 0; per-tag breakdown; comparison to grpo_300 (0.320 test), with no ranking claim from one seed.

### 2026-11-12 — main run 1 results (1 seed): GRPO learns conflict resolution; OPSD collapsed
**GRPO (full fine-tuning, 300 steps, v3, seed 0, final checkpoint):** train reward 0.243 (first 25 steps) → 0.366 (last 25). Held-out:

| | val EM | test EM |
|---|---|---|
| grpo_300 | 0.327 | 0.320 |
| prompted_1.7b (same model, untrained) | 0.194 | 0.211 |
| Δ, paired bootstrap 95% CI | **+0.132 [+0.107, +0.159]** | **+0.109 [+0.082, +0.137]** |

Preregistered learning-signal criterion **met**. By question type (test, untrained → GRPO): out_of_order 0.215 → **0.403**, relative_date 0.193 → 0.322, xref_date 0.200 → 0.322, alias 0.213 → 0.296, unreliable 0.190 → 0.270, plain 0.393 → 0.250. Memory length barely changed (154 → 159 tokens). **Unlike the 100-step pilot, the gains come from conflict resolution, not format**; plain slots lose, consistent with reallocating the budget toward conflicted facts. Still below the size-matched-or-larger pipelines: −0.166 [−0.203, −0.126] vs 4B extraction + rules, −0.463 vs 32B session-context extraction + rules. One seed: no claim about stability.

**OPSD (derivable-hint self-teacher): collapsed, stopped at step ~50 of 300.** By 5-step blocks, reward 0.20 → 0.23 → 0.22 → 0.20 → 0.15 → 0.05 → 0.02 → 0.007 → 0.004; completions hit the 256-token cap from step ~20; the KL loss fell 0.29 → 0.004. Diagnosis: the teacher is the *current* policy, so as the student degenerates the teacher degenerates with it, and the KL becomes trivially small (the known moving self-teacher failure; cf. "OPSD with Teacher Evolution", E²-OPSD entropy overshoot). Run stopped to save ~2.5 GPU-hours; no checkpoint kept. **Fix (next):** a frozen teacher (initial weights with hints). Since a second model copy does not fit on GPU 0, serve the frozen base model on GPU 1 and use the per-token reverse-KL estimator on sampled tokens (teacher log-prob of the sampled token via vLLM sequence log-probs), as in on-policy distillation. This is a design change made after observing the failure, recorded here before the rerun.

### 2026-11-12 — main run 1 preregistration (written before the run; owner chose "train on v3")
- **OPSD smoke test (10 steps, v3):** 36.5 s/step (teacher forward roughly doubles the backward phase), 21.1 GB peak, no NaN, KL loss 0.30 flat at 10 steps, completion length 220 → 230 tokens (watch: the teacher may favor longer memories, which the 160-token budget truncates).
- **Runs:** full fine-tuning (no LoRA), Qwen3-1.7B, v3 `train_2s`, 300 steps, seed 0, lr 1e-6, β = 0 (no KL; a reference model does not fit on GPU 0), 32 trajectories/step. **GRPO** (global trajectory advantage, 4 episodes × group 8) and **OPSD** (32 episodes × 1, derivable hints). `scripts/main_v3_run1.sh`.
- **Eval:** final checkpoint (no checkpoint selection), greedy writer, frozen Qwen3-4B reader, v3 val and frozen test.
- **Criteria:** (1) learning signal = trained − prompted_1.7b (test 0.211) with paired bootstrap 95% CI excluding 0; (2) per-difficulty breakdown (xref_date, relative_date, unreliable, alias, out_of_order) to tell conflict resolution from format gains; (3) report the gap to extract_rules_32b_ctx (0.783) as reference, with no threshold. One seed: no GRPO-vs-OPSD ranking claim.

### 2026-11-12 — gate v3 result: MARGINAL PASS (1 seed, 300 frozen test episodes)
Commands: `scripts/gate_v3.sh`, then `scripts/gate_v3_rerun.sh` after the extraction-cap fix below. Data `episodes_v3` (seed 2029): labels re-derived from text with 0 mismatches; paraphrase fallback 8.6% test / 8.1% val / 8.0% train; **faithfulness 2/400 unfaithful (0.5%, Wilson [0.14%, 1.8%])**.

| arm | val EM | test EM |
|---|---|---|
| oracle (privileged) | 0.998 | 0.997 |
| **extract_rules_32b_ctx** (32B, whole session as context per line) | — | **0.783** |
| extract_rules_32b (32B, per line + session date) | — | 0.681 |
| extract_rules (4B, per line + session date) | 0.448 | 0.486 |
| prompted Qwen3-1.7B | 0.194 | 0.211 |
| bm25 | 0.177 | 0.197 |
| prompted Qwen3-4B | 0.194 | 0.178 |
| prompted Qwen3-32B-AWQ | — | 0.151 |
| write_all | 0.096 | 0.092 |
| newest_wins / symbolic | 0.053 | 0.048 |
| no_memory | 0.000 | 0.000 |

**Gate (test, all non-privileged arms):** strongest = extract_rules_32b_ctx; oracle − strongest = **0.214**, paired bootstrap 95% CI **[0.194, 0.234]**. PASS on the point estimate (the rule `headroom_gate.py` applies), but **the interval straddles 0.20**: a marginal pass.

**Readings:** (1) Cross-referenced dates work as designed against per-line extraction: answer-in-memory for asked slots with a cross-referenced date is 0.677 (32B per line) vs 0.911 without; with whole-session context it recovers to 0.846. (2) Every structured conflict added so far (v1 paraphrase, v2 budget/conflicts, v3 dates) has been largely solvable by a large model that parses with full context plus fixed rules. The remaining headroom over the strongest pipeline is ~21 points. (3) Small prompted writers stay near 0.2 at every version, so headroom over size-matched baselines is large (≥ 0.5 over the prompted 1.7B/4B and the 4B pipeline). Whether to train now on a marginal gate is an owner decision.

### 2026-11-12 — gate v3 harness fix (before any v3 gate number was computed)
The 32B per-line extractor parsed only 83.6% of v3 test lines. Diagnosis on 300 random test lines: with relative dates it writes date arithmetic before the JSON, and the extractor's 160-token output cap truncated it (49/300 unparseable at 160 tokens, **0/300 at 1,024**). This is a harness flaw that weakens the strongest baseline, so `extract.py` now caps output at 1,024 tokens for **all** extraction arms, and the 4B, 32B and 32B-context arms are rerun on v3 val/test. The diagnosis also shows the expected v3 effect: per-line extraction guesses cross-referenced dates (e.g. it assumes the referenced report is on the session date). No v3 reader score or gate had been computed when this fix was made.

### 2026-11-12 — OPSD arm designed + implemented (not yet run)
Owner decision: add on-policy self-distillation (Zhao et al. 2026, arXiv 2601.18734) as a training arm. Design (`hints.py`, `writer.build_teacher_prompt`, `grpo_full.py --algo opsd`): the teacher is the same current writer with **hints derivable from the stream so far**: resolved absolute dates per statement, aliases introduced so far, and the unreliable source only once its audit line has appeared. Checked on 2,000 v3 train episodes: the unreliable-source hint appears 0 times before its audit and in all 2,522 sessions after; every statement date resolves; no answer appears in any note. Loss: per-token full-vocabulary reverse KL(student‖teacher) on student samples; 32 trajectories/step (32 episodes × 1) to match GRPO's sampling budget; reader reward logged only. Rationale: dense per-token signal instead of a 6-question EM reward (the 100-step GRPO pilot learned format, not conflicts); no extra weights in memory (teacher = policy).

### 2026-11-12 — gate v3 preregistration (written before the v3 run; owner chose "harder conflicts")
- **Change from v2 (dates only):** seed 2029, same split/exclusions/slots/conflict questions. Each session opens with `Session date: <date>`. Each statement's date is absolute (~40%), relative to the session date (~35%: "N days ago", "N weeks ago", "earlier today"), or **relative to an earlier statement in the same session** (~25%: "N days after Source-X's report on Y"; anchors are unique (source, name) pairs within the session). Explicit audit lines are unchanged. Labels: `scripts/check_v3_labels.py` re-derives all 15,600 asked-slot answers from the text: **0 mismatches, 0 ambiguous references.**
- **Hypothesis:** per-line extraction cannot resolve cross-referenced dates, so extraction + rules falls below the oracle by ≥ 0.20 even with a 32B extractor; a writer that keeps state can resolve them.
- **Arms.** val: oracle, no_memory, write_all, newest_wins, symbolic, bm25, extract_rules (4B, per line + session date), prompted 1.7B, 4B. **test (decides the gate):** the same plus **extract_rules_32b** (32B, per line + session date) and **extract_rules_32b_ctx** (32B, whole session shown as context for every line, so cross-references can be resolved), and prompted 32B. Reader, budget 160, thresholds unchanged.
- **Gate:** test oracle ≥ 0.90 and oracle − strongest of ALL non-privileged arms (incl. both 32B extraction variants) ≥ 0.20. Faithfulness: 32B judge on 400 test lines, ≤ 2%.
- **Limitation:** the session-context 32B extractor is close to a large prompted pipeline; if it closes the gap, v3's difficulty is again "parsing with context", and the owner decides the framing.

### 2026-11-12 — gate v2 REVISED: FAIL under the stricter 32B-extractor check
Same pipeline as `extract_rules`, with Qwen3-32B-AWQ as the extractor (`extract.py --model Qwen/Qwen3-32B-AWQ`), on the frozen v2 test set. Extraction accuracy: value 0.954 (4B: 0.880), subject 0.938, relation valid 0.974, source 1.000, date 1.000. **Test EM 0.805.** Gate over all non-privileged arms: strongest = extract_rules_32b, oracle − strongest = **0.193**, paired bootstrap 95% CI [0.174, 0.214] → **FAIL** (threshold 0.20, unchanged). As stated before this check ran, the v2 verdict is revised to FAIL.

**Interpretation:** v2 conflicts are mostly an extraction problem. Once a strong model parses each line, fixed rules (aliases, latest date, drop sources caught by an audit) resolve most of them. Per the design ("do not train on a failed gate"), conflicts must get harder before main training. The candidate changes are listed in HANDOFF (A6b) and need an owner decision.

### 2026-11-12 — gate v2 result: PASS vs the preregistered arms (superseded above)
Commands: `scripts/gate_v2.sh` (driver log and outputs in `$S/runs/gate_v2/`). Data: `episodes_v2` (seed 2028), 2,000 train / 300 val / 300 test, all validated, splits pairwise subject-disjoint, 0 FactConsolidation-6K subjects. Paraphrase fallback 8.1% test / 7.6% val / 7.5% train.

**Paraphrase faithfulness:** Qwen3-32B-AWQ judged 400 random paraphrased test lines: 3 unfaithful (0.75%, Wilson 95% [0.26%, 2.18%]), under the 2% bar. One real error (a source name turned into an alias); two turned "as of DATE" into "on DATE".

**Extraction accuracy (Qwen3-4B, per fact line vs privileged metadata), val / test:** value 0.876 / 0.880, subject 0.933 / 0.949, relation valid 0.930 / 0.951, source 1.000 / 1.000, date 0.999 / 1.000.

| arm | val EM | test EM |
|---|---|---|
| oracle (privileged) | 0.991 | 0.998 |
| **extract_rules** (Qwen3-4B extraction + rules) | **0.602** | **0.632** |
| prompted Qwen3-1.7B | 0.183 | 0.218 |
| bm25 (question-aware) | 0.203 | 0.192 |
| prompted Qwen3-4B | 0.177 | 0.174 |
| prompted Qwen3-32B-AWQ | 0.171 | 0.168 |
| write_all | 0.111 | 0.106 |
| newest_wins | 0.079 | 0.084 |
| symbolic (template regex) | 0.079 | 0.084 |
| no_memory | 0.000 | 0.000 |

**Gate (test):** strongest non-privileged = extract_rules; oracle − strongest = **0.366**, paired bootstrap 95% CI [0.339, 0.393] → **PASS** (oracle ≥ 0.90, headroom ≥ 0.20). Val agrees (0.389).

**Readings and caveats:** (1) The prompted 32B writer is *worse* than the 1.7B at this budget: it spends tokens on alias lines and source tags and loses facts to truncation (answer-in-memory 0.19 on val vs 0.31 for 1.7B). Scale alone doesn't help. (2) extract_rules' remaining gap is mostly extraction error (12% wrong values with a 4B extractor); with perfect extraction, rules reach the oracle (v0). A stricter post-hoc check with a **32B extractor** is running and will be reported here; if it lands within 0.20 of the oracle, the gate verdict is revised. (3) One generator seed, one paraphrase seed; reader, paraphraser and extractor share the Qwen3 family.

### 2026-11-12 — full fine-tuning path (HANDOFF item 7): implemented + timed
`stalestream/grpo_full.py` + `scripts/full_ft_timing.sh`. No LoRA: trainer on GPU 0 (fp32 master weights, bf16 autocast, 8-bit AdamW, lr 1e-6, gradient checkpointing); writer sampler = vLLM server on GPU 1 receiving bf16 weights over NCCL after every step (TRL `VLLMClient`); reader server also on GPU 1. 20 steps on v1 train (4 episodes × group 8, 2 sessions, β = 0): **21.4 s/step** (rollout 5.0, reward 1.4, backward 14.5, weight sync 0.5), peak 21.1 GB on GPU 0, no NaN, 2.5% zero-variance groups, mean pre-clip grad norm 3.9 (clip at 1.0 active). 300 steps ≈ 1.8 h. **KL (β > 0) not yet measured:** the bf16 reference model (+3.4 GB) likely does not fit beside 21.1 GB; options are the reference on GPU 1 with a smaller reader allocation, or β = 0. Timing only, no learning claim (reward 0.208 → 0.242, first vs last 5 steps).

### 2026-11-12 — reproducibility note
The v1 data on disk was produced by an uncommitted generator state with a different RNG draw order. `generator.py --rng-order v1` now reproduces v1_raw byte-identically (seed 2027, `--date-style mixed`); v0 still reproduces with the default order. v2 data uses the default order.

**Not yet built:** BM25, prompted Qwen3-32B writer, consistency-check defense, privileged resolver, keep/drop controller, RFT, injections, held-out readers.

## Canonical CS258 project documents

- [Project proposal](./CS258_Project_Proposal.md) ([original DOCX](./CS258_Project_Proposal.docx); [Google Drive source](https://docs.google.com/document/d/17jOimeZCTgH-18bdfjEmTVXh46eGe8GB/edit))
- [Design document](./CS258_Design_Doc.md) ([original DOCX](./CS258_Design_Doc.docx); [Google Drive source](https://docs.google.com/document/d/1LrRCf8crBVCljb5nkpis7SB3N10L8g87/edit))

These copies capture the source documents at commit time. For subsequent edits, reconcile against the Google Drive sources before treating the snapshots as current.
