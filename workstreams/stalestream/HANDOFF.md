# StaleStream — agent handoff (2026-11-12)

Read this, then `STATUS.md` (evidence log), `README.md` (commands), `CS258_Design_Doc.md`
(design). This file is the work queue. Keep it current: tick items, add evidence to STATUS.

## Rules that bind you
- **This repo is public.** Never commit private code. `headroom_gate.py` comes from private
  `Vedant2100/f26@1b30fd7` and is git-ignored here; copy it locally (README).
- **Preregister before running** (hypothesis, arms, split, seeds, budget) in STATUS, commit, then run.
- **Gate thresholds never move:** oracle ≥ 0.90 EM and oracle − strongest non-trained baseline ≥ 0.20, on frozen test episodes.
- **Test set is for final numbers only.** Tune on the validation split (item 1). The v1 test set has
  already been used for the gate and the pilot.
- Don't generate a new environment version after looking at trained-policy results on it without
  saying so in STATUS; every environment version gets a fresh, frozen test set.
- Separate designed / implemented / executed / replicated. One seed is not replication.
- GPU use on the local 2× A30 machine is authorized by the owner; anything paid (APIs, Modal) is not.

## Current state (audited 2026-11-12, `scripts/audit.py`: 0 failures)
- **Built:** generator (v0 templated, v1 paraphrased), rule baselines + symbolic resolver,
  prompted writer, frozen Qwen3-4B reader, multi-session GRPO/RLOO loop (LoRA), paraphraser, audit.
- **v0:** gate FAIL. Symbolic resolver = oracle (0.999).
- **v1 (paraphrased):** gate PASS vs template baselines (gap 0.776), but the strongest relevant
  baseline (LLM extraction + rules) is **not built**. Paraphrases are light, so this baseline may close the gap.
- **Pilot (exploratory, 1 seed, 100 steps):** GRPO 0.252, RLOO 0.251 vs untrained 0.222 on v1 test.
  Gains are on non-conflict slots plus shorter memories; conflict slots barely move. RL learned
  format/budget, not conflict resolution.
- **Data and runs** live only on the original machine (`/scratch/vbork001/stalestream`). Regenerate
  with the README commands: generator seeds 2026 (v0), 2027 (v1), paraphrase seed 7. Generation is
  deterministic; vLLM sampling is only approximately reproducible.

## Decisions already made by the owner
- Main comparison: **GRPO vs DPO**, with **RFT** as the supervised baseline (agreed with the course
  instructor by email). **OPSD added as a training arm** (owner, 2026-11-12), with hints-only privileged
  information. RLOO only if time permits. Keep/drop controller dropped.
- **No LoRA:** switch to full fine-tuning (matches Memory-R1 / Mem-α).
- Baselines promised: no memory, oracle, BM25, newest-wins, LLM extraction + rules, prompted
  Qwen3-1.7B and Qwen3-32B writers, RFT. Evaluation: held-out entities, one held-out reader,
  FactConsolidation. Injections optional.

## Work queue (in order; each has a done-criterion)
Parallelism: A (gate v2) mostly needs GPU 1 (extraction model, 32B check); B7 (full fine-tuning
timing) needs GPU 0. They can run at the same time.

### A. Before any more training (blocking)
1. **[DONE]** **Validation split.** Three-way entity-disjoint split (train/val/test) by subject hash, without
   moving current test subjects. Done when audit.py checks all three are disjoint.
2. **[DONE: v2, seed 2028; faithfulness 0.75% unfaithful]** **Gate v2 environment.** Fresh episodes (new seed), frozen test set:
   - Binding budget: the oracle uses ~99 of 160 tokens. Raise facts per episode or lower the budget
     until the oracle is near the cap and still ≥ 0.90.
   - Conflict-heavy questions: most asked slots have an unreliable, out-of-order or alias feature.
   - Paraphrase faithfulness check: an LLM judge on ≥ 300 random lines (paraphrase entails the original;
     same relation, value, date, source). Report the error rate; regenerate if > 2%.
3. **[DONE: `extract.py`; 4B 0.632 test EM; 32B-extractor check pending]** **LLM extraction + rules baseline.** An LLM (Qwen3-4B, no thinking) converts each line to
   (subject, relation, value, date, source) JSON; reuse `baselines.resolve` + audit-flag logic.
   Report extraction accuracy against the hidden labels on validation.
4. **[DONE: 0.192 test]** **BM25 baseline** (`rank_bm25` is installed): retrieve top-k statements by question, budget-truncate, read.
5. **[DONE: AWQ fits one A30 at 0.93 util (KV ~4.4k tokens, slow); 0.168 test]** **Prompted Qwen3-32B writer.** Test that a 4-bit (AWQ) version fits one A30 with vLLM; thinking off.
6. **[DONE: PASS vs preregistered arms (gap 0.366); FAIL vs 32B extraction + rules (0.805, gap 0.193)]** **Run gate v2** on the frozen test set with all non-trained arms. If extraction + rules is within
   20 points of the oracle, stop and redesign conflicts (e.g. reliability inferred from contradiction
   patterns instead of an explicit audit line, relative/implicit dates). Don't train on a failed gate.

6b. **[DONE: v3 (relative and cross-referenced dates), seed 2029; MARGINAL PASS, gap 0.214 [0.194, 0.234] vs 32B session-context extraction + rules]** **Harder conflicts (v3).** Rules over near-perfect extraction already reach
   0.80, so the remaining headroom is small. Make conflicts that per-line extraction plus fixed rules
   cannot resolve. Candidates:
   - Unreliable sources revealed only by contradiction patterns (e.g. a source repeatedly
     disagreeing with later verified facts) instead of an explicit audit line.
   - Relative or implicit dates ("two months after Source-B's report", "earlier this year").
   - Facts whose validity depends on another fact (multi-hop: the question asks about X's spouse's
     country, so the writer must keep both links current).
   - Partial retractions ("Source-A now says its 2023 report on X was mistaken").
   Rerun the gate with the 32B-extractor arm included from the start.

### B. Training (after the gate passes)
7. **Full fine-tuning path** for `grpo.py`: policy on GPU 0 (bf16, gradient checkpointing,
   8-bit or bf16 Adam), writer sampler and reader both on GPU 1, weight sync each step (TRL vLLM
   server-mode sync or equivalent), KL penalty to the reference model. Done when a 20-step run
   completes, with s/step recorded. The submitted proposal text may say "with LoRA"; tell the owner
   so the Google Doc gets a one-line note when this lands.
   **Status: DONE for β = 0** (`grpo_full.py`, `scripts/full_ft_timing.sh`; 21.4 s/step, 21.1 GB peak).
   Open: KL. The reference model does not fit beside the trainer on GPU 0. Either move it to GPU 1
   (lower the reader to ~0.40) or run β = 0 and say so.
8. **Sample bank → RFT + DPO.** Base writer samples G=8 per state; pairs share the same prompt
   (per-session shared-prefix states, finished greedily to score). Match GRPO's sampling budget
   (steps × 32 trajectories). DPO keeps pairs with a reward gap ≥ 2/6.
8b. **OPSD arm (owner decision 2026-11-12; implemented, not yet smoke-tested).** On-policy self-distillation
   (Zhao et al., arXiv 2601.18734): `grpo_full.py --algo opsd`. The student is the writer; the teacher is the
   same current model (gradient-free) prompted with **derivable hints only** (`hints.py`): resolved absolute
   dates for the current session's statements, aliases introduced so far, and the unreliable source only
   after its audit line has appeared. Never answers or oracle memory (limits "privilege illusion").
   Loss: per-token full-vocabulary reverse KL(student‖teacher) on student rollouts. Budget matched to
   GRPO: 32 trajectories/step as 32 episodes × 1. Reader reward logged for monitoring and checkpoint
   selection only. Next: `ALGO=opsd DATA=$S/data/episodes_v3 TAG=_opsd STEPS=10 scripts/full_ft_timing.sh`
   once the gate passes. Possible later ablation: hints vs answers as privileged information.
8c. **Shared-memory local groups for GRPO (Memory-R2's LoGo-GRPO, arXiv 2605.21768).** Once rollouts write
   different session-1 memories, their later rewards are not comparable (different effective
   environments), so plain trajectory-level GRPO gives biased credit. Add a local branch: from one
   sampled intermediate memory, roll out G candidates for the next session, finish greedily, and compute
   group-relative advantages within that shared state, alongside the global trajectory advantage.
   Reuse the shared-state machinery of the DPO bank (item 8). Ablate global-only vs global+local.
8d. **Session-length curriculum.** Train 2 → 3 → 4 sessions (Memory-R2: without a horizon curriculum,
   long-horizon training collapsed). Select each stage's checkpoint on val.
8e. **Per-session verifiable reward (ablation, not default).** After each session, the fraction of
   currently valid facts (truth as of that session, from hidden labels) whose correct value appears in
   memory. Dense and needs no learned verifier (cf. TrustMem 2606.25161, AiO-Mem 2610.21147).
   The 160-token budget limits stuffing. The default reward stays reader EM.
9. **Main runs:** GRPO 300 steps × 3 seeds; DPO and RFT × 3 seeds; model selection on validation only.
   RLOO only if time permits. Its advantages are unnormalized (~6× smaller gradients than GRPO at
   the same lr), so either tune its lr on validation or report the effective-step-size difference.
10. **Held-out reader** (different model family) on final test memories.

### C. Evaluation and writing
11. **FactConsolidation** (MemoryAgentBench, built from MQuAKE): remove its entities from training
    first; 6K single-hop version; report the memory budget used.
12. **Injections (optional, only if time):** held-out MemPoison-style attack families; writer trained
    with vs without injections vs a static consistency-check defense.
12a. **Related work update.** The proposal line "RL writers like Memory-R1 and Mem-α don't handle stale
    facts" is dated: cite Memory-R2, TrustMem, LifeFuse-Mem, AiO-Mem (2026) and narrow the gap claim to
    conflict resolution under dates and source reliability.
13. Update the Google Doc design (compute = 2× A30; DPO added; optional items marked). The owner does this.

### D. Housekeeping
14. Open a PR for `agent/stalestream/v0-env` (the owner or coordinator merges it).
15. The original machine has a local-only branch `backup/pre-push-rewrite` (pre-rewrite history,
    including the gate file). Delete it once the PR is merged.
16. Update STATUS as each item lands (evidence, commands, numbers), and tick this queue.

### E. Later (after RL shows real conflict-resolution gains)
17a. **PPO (optional, owner 2026-11-12).** A separate critic does not fit (GPU 0 at 21 GB with full
    fine-tuning). Options: a value head on the policy trunk, or VinePPO-style Monte Carlo values from
    shared-state rerollouts (reuses item 8c). Memory-R1 found GRPO ≥ PPO, so this is a comparison
    point, not an expected win.
17b. **Learned reward models (optional).** (i) Bradley-Terry reward model trained on the DPO preference
    pairs, then RL against it: compares DPO vs RM+RL on the same preference data. (ii) A learned
    per-session process reward model (cf. AiO-Mem): lowest priority, since 8e already gives a
    verifiable per-session score.
17. **Weight-space programming comparison.** A frontier LLM edits the writer's weights from a
    plain-language memory policy, without gradients (MIT CSAIL, Nov 2026:
    https://rikiyat.github.io/blog/weight-space-programming/). Compare against GRPO/DPO on the same
    held-out episodes. This tests whether RL's gains are only "obstacle removal" (format/budget).
    Needs paid frontier-API access: ask the owner first. Not part of the CS258 proposal.

## Known machine pitfalls (original machine)
- Home has a hidden ~11 GB cap. Everything heavy goes on `/scratch`; `source /scratch/vbork001/stalestream/env.sh`.
- Shell has `noclobber`: use `>|` to overwrite logs.
- vllm ≥ 0.33 is not installable (glibc 2.28). Use vllm 0.21 on Python 3.12. Triton needs `CPATH` from env.sh.
- Don't put a per-request `seed` in vLLM `SamplingParams` during RL: all G samples become identical.
- `pkill -f <pattern>` kills its own shell when the pattern is in the command line; killed runs can
  leave an orphan `VLLM::EngineCore` holding GPU memory (check `nvidia-smi`).
- RLOO advantages are unnormalized: ~6× smaller gradients than GRPO at the same lr.
- Two vLLM servers on one GPU must start one after the other (concurrent startup miscounts memory).
- A killed driver script can leave the `vllm serve` process alive (parent re-assigned to PID 1).
  Check `nvidia-smi --query-compute-apps=pid,used_memory --format=csv` before starting GPU work.
- FactConsolidation-262K contains essentially every MQuAKE-CF-3k subject, so only the 6K version can
  be made entity-disjoint from training (its 160 subjects are excluded from v2).
