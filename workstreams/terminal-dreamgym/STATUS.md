# Terminal DreamGym Agent

**Area:** Autonomous Research & Self-Improvement
**Source:** https://github.com/Vedant2100/terminal_dreamgym
**Owner agent:** `terminal-dreamgym`
**Current state (2026-11-12):** matched evaluation EXECUTED (one preregistered run, 3 seeds); null primary result. Source changes in [terminal_dreamgym PR #1](https://github.com/Vedant2100/terminal_dreamgym/pull/1), not merged.

## Research aim
Establish held-out and adversarial transfer beyond naive reflection.

## Evidence handoff (2026-11-12)

- **Source:** branch `fix/matched-eval`, results commit `2879481` (protocol committed earlier at `e935543`, run code at `92bfda0`).
- **Goal:** do the four handwritten skill texts raise Qwen2.5-7B strict success over no skill text when every condition gets the same model, sampling, attempt budget and scoring?
- **Controls:** `no_skill`, length-matched `placebo`, bad-advice `symptom_patch` (formerly `reflection_only`). Conditions differ only in the prompt's skill block.
- **Tasks / seeds:** all 100 tasks (20 base tasks × 5 near-identical variants), seeds 1–3, up to 3 attempts per task, temperature 0.7, `qwen2.5:7b` via Ollama, one RTX 2080 Ti, 71 min.
- **Commands:** `sbatch scripts/matched_eval.sbatch runs/matched_eval.jsonl --seeds 1,2,3`; `python -m terminal_dreamgym.cli matched-report`.
- **Raw results:** `runs/matched_eval.jsonl` (1,200 records, 0 infrastructure errors), `reports/matched_eval.md`.
- **Strict success** (target test passes and no previously passing test breaks; 19 base tasks after excluding one that passes before any edit): no_skill 0.512, handwritten 0.572, placebo 0.530, symptom_patch 0.442.
- **Primary comparison:** handwritten − no_skill = +0.060, 95% CI [−0.028, +0.151] (bootstrap over base tasks); 6 better / 4 worse / 9 tied. No detectable difference.
- **Secondary (uncorrected):** handwritten − placebo +0.042 [−0.049, +0.147]. The adversarial-split gain (+0.144) also appears for placebo − no_skill (+0.133), so it tracks extra prompt text rather than skill content. Skills cut unparseable replies from 27% to 11%.
- **Verification:** all 1,200 runs re-scored from saved sandboxes (`scripts/reverify_matched.py`), all match. Reference fix makes all 20 task repos solvable.
- **Reconciliation of earlier evidence:** the July demo gave the baseline 1 attempt and skills 3. The "two-seed sweep" (`runs/evaluation.json`) was unit-test mock data, not a model run. Three tests per dependency repo were unsolvable (generator bug, now fixed).
- **Run 1 aborted** at 108/1,200 records before analysis (unsolvable tasks, timeout crash path, repeated seeds); recorded in the protocol's Deviations section.

## What is supported / not supported
- Supported: fixed handwritten skill prompts give no detectable gain on this benchmark for Qwen2.5-7B.
- Not supported: any claim of self-improvement. Diagnosis is rule-based and skills are fixed handwritten text; no model writes them.
- Limits: held-out tasks share repos with train tasks; the pass-to-pass check is empty for 14 of 19 base tasks; 9 of 19 base tasks tie across all conditions, so power is low.

## Next decisive action
Model-written skills (approved by the user 2026-11-12): the model writes `SKILL.md` from its own failure traces, evaluated under the same protocol with a leave-one-family-out split so skills are never tested on the repo they were written from.

## Do not overclaim
A null result for handwritten prompts says nothing yet about model-written skills or RL.
