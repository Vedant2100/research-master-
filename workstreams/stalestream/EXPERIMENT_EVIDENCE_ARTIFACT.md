# StaleStream — experiment evidence and trace inventory (2026-11-14)

This is the complete experiment record recoverable from the committed STATUS.md and run scripts as of commit 2816b12a4a6b2c54fcf1b569d7f82d325be1576f. It is **not** a raw per-episode trace dump. Raw run outputs remain on the BCC scratch filesystem and must be exported before a true trace viewer can be built.

## Experimental question

Can a small model learn to maintain a bounded memory across sequential sessions when facts change, conflict, or require date/source reasoning, using downstream reader answer accuracy as the reward?

Pipeline:
1. Conversation stream arrives over multiple sessions.
2. Either a writer directly produces compact memory, or an extractor converts individual lines into structured facts.
3. Fixed rules resolve aliases, source reliability, and temporal ordering.
4. A frozen Qwen3-4B reader answers questions using only the memory.
5. Reader exact-match accuracy is the reward and evaluation metric.

Memory budget: 160 tokens. Training episodes contain two sessions; held-out test episodes contain three to four sessions. Entity-disjoint train/validation/test splits are used for v3.

## Environment and gate history

| Version | Main change | Strongest non-trained baseline | Oracle | Gap to oracle | Decision |
|---|---|---:|---:|---:|---|
| v0 | Templated facts | Symbolic resolver 0.999 | 0.999 | 0.000 | Fail: rules solve the task |
| v1 | Mixed date formats and paraphrased lines | Prompted 4B writer 0.223 | 0.999 | 0.776 | Pass, but strong extraction baseline missing |
| v2 | More facts, tighter budget, conflict-focused questions | 32B extraction + rules 0.805 | 0.998 | 0.193 | Fail: strongest baseline too close |
| v3 | Relative and cross-referenced dates | 32B session-context extraction + rules 0.783 | 0.997 | 0.214 | Marginal pass; 95% CI [0.194, 0.234] |

The gate threshold remains oracle EM ≥ 0.90 and at least 0.20 headroom over the strongest non-privileged baseline. The v3 point estimate passes; its confidence interval crosses the threshold.

## v3 non-trained baselines

| Arm | Validation EM | Test EM |
|---|---:|---:|
| Oracle (privileged) | — | 0.997 |
| Extract + rules, Qwen3-32B with full session context | — | 0.783 |
| Extract + rules, Qwen3-32B per-line + session date | — | 0.681 |
| Extract + rules, Qwen3-4B with session context | 0.448 | 0.486 |
| Prompted Qwen3-1.7B writer | 0.194 | 0.211 |
| BM25, question-aware | 0.177 | 0.197 |
| Prompted Qwen3-4B writer | 0.194 | 0.178 |
| Prompted Qwen3-32B-AWQ writer | — | 0.151 |
| Write all | 0.096 | 0.092 |
| Newest wins / symbolic | 0.053 | 0.048 |
| No memory | 0.000 | 0.000 |

## Writer training arms

All arms use the frozen Qwen3-4B reader. RFT and DPO use the downstream reader reward to select training examples/pairs; GRPO uses the same reader reward on-policy.

| Arm | Val EM | Test EM | Evidence |
|---|---:|---:|---|
| Untrained 1.7B writer | 0.194 | 0.211 | Baseline |
| RFT | 0.212 | 0.211 | One seed; no improvement |
| DPO | 0.210 | 0.223 | One seed; small, uncertain improvement |
| Frozen-teacher OPSD | 0.211 | 0.206 | One seed; no downstream gain |
| GRPO seed 0 | 0.327 | 0.320 | One seed result |
| GRPO seeds 0/1/2 mean ± SD | 0.299 ± 0.031 | 0.292 ± 0.026 | Three seeds; each seed's test CI excludes zero vs untrained |

Writer GRPO improved test EM by +0.081 on average over the untrained writer. RFT/DPO/OPSD stayed near baseline. The frozen-teacher OPSD run was stable, but the hinted teacher was no better than the student, so the null result does not establish that distillation is ineffective.

## Extractor training arms — header context

The extractor generates structured facts line by line; fixed rules and the frozen reader are unchanged.

| Arm | Relation-valid (test) | Val EM | Test EM |
|---|---:|---:|---:|
| Untrained 1.7B extractor | 0.63 | 0.283 | 0.259 |
| RFT | 0.79 | 0.393 | 0.380 |
| DPO | 0.91 | 0.470 | 0.469 |
| GRPO, three seeds | 0.97 | 0.696 ± 0.029 | 0.691 ± 0.011 |

Paired bootstrap for extractor RFT and DPO versus untrained (test; validation):
- RFT: +0.121 [0.094, 0.146]; +0.109 [0.081, 0.136].
- DPO: +0.209 [0.178, 0.241]; +0.187 [0.158, 0.215].
- RFT versus GRPO seed mean: −0.311 [−0.336, −0.283] test.
- DPO versus GRPO seed mean: −0.222 [−0.249, −0.196] test.

These do not support a definitive algorithm ranking: RFT/DPO each have one seed, untuned hyperparameters, and an offline base-model bank; GRPO has three on-policy seeds.

### Extractor DPO/RFT bank details

- 800 training episodes.
- 26,044 line groups.
- 208,352 candidate samples (8 per group).
- 9,504 unique memories scored.
- 8.8% of groups had reward variance.
- 2,294 RFT examples (mean reward 0.40).
- 2,294 DPO pairs (mean reward gap 0.19).
- DPO pair construction: same-prompt best versus worst candidate, retaining pairs with reader-EM gap ≥ 1/6.
- Current DPO settings inherited from writer arm: beta 0.1, learning rate 1e-6, one epoch.

The reward is the same downstream reader EM used by GRPO. DPO receives a pairwise preference derived from that scalar reward; it does not optimize a separate relation-validity reward. Its limitation is the offline base-policy sample distribution and sparse within-group reward variance.

## Extractor GRPO — three-seed header-context result

| Seed | Val EM | Test EM |
|---|---:|---:|
| 0 | 0.704 | 0.688 |
| 1 | 0.664 | 0.681 |
| 2 | 0.720 | 0.703 |
| Mean ± SD | 0.696 ± 0.029 | 0.691 ± 0.011 |

Paired bootstrap, seed mean:
- Versus untrained 1.7B extractor: +0.431 [0.406, 0.457] test.
- Versus GRPO writer: +0.399 [0.376, 0.421] test.
- Versus 4B session-context extraction + rules: +0.153 [0.124, 0.182] test.
- Versus 32B session-context extraction + rules: −0.092 [−0.115, −0.068] test.

Training reward for seed 0 rose from approximately 0.32 to 0.70.

### Where the GRPO extractor gain comes from

| Diagnostic | Untrained | GRPO |
|---|---:|---:|
| Relation label valid | 0.63 | 0.97 |
| Value extraction | 0.90 | 0.95 |
| Subject extraction | 0.91 | 0.95 |
| Date extraction | 0.68 | 0.70 |

Per-tag test EM (untrained → GRPO; 32B session-context reference):
- Plain: 0.36 → 0.88 (32B: 0.79).
- Alias: 0.24 → 0.69 (32B: 0.78).
- Out-of-order: 0.27 → 0.69 (32B: 0.80).
- Unreliable source: 0.25 → 0.68 (32B: 0.80).
- Relative date: 0.29 → 0.69 (32B: 0.82).
- Cross-referenced date: 0.22 → 0.57 (32B: 0.74).

Interpretation: the largest extraction gain is relation-grammar mapping; date accuracy barely changes. The cross-referenced-date weakness remains material.

## What is not yet in this artifact

The committed STATUS.md contains aggregate results and selected training summaries, not complete per-episode prompts, completions, memories, reader answers, or every optimization step.

The scripts specify these raw output locations:
- Header-context extractor GRPO: $S/runs/main_v3_grpo_extract/
- Extractor round 2 (RFT/DPO bank and session-context GRPO): $S/runs/extractor_round2/

In the run scripts, $S=/scratch/vbork001/stalestream. The round-2 directory is expected to contain bank_raw.jsonl, bank_scored.jsonl, bank/, progress.log, rft.log, dpo.log, ctx_s{0,1,2}.log, ctx_s{0,1,2}/train_log.jsonl, model checkpoints, memory JSONL files, and reader-evaluation JSONL files. The header-context GRPO directory contains per-seed training logs, memory JSONL files, evaluation JSONL files, and server/progress logs.

Those files were not present in the public GitHub branch when this artifact was assembled. A true complete trace artifact requires exporting and verifying them from BCC. Do not represent this summary as the full raw trace dump.
