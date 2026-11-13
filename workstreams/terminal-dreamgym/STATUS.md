# Terminal DreamGym Agent

**Area:** Autonomous Research & Self-Improvement
**Source:** https://github.com/Vedant2100/terminal_dreamgym
**Owner agent:** `terminal-dreamgym`
**Current state (2026-11-12):** two preregistered experiments EXECUTED, both null: handwritten skills (3 seeds, replicated with 5) and model-written skills (5 seeds). Source changes in [terminal_dreamgym PR #1](https://github.com/Vedant2100/terminal_dreamgym/pull/1) and the model-written-skills PR (branch `feat/model-written-skills`), neither merged.

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

## Evidence handoff: model-written skills (2026-11-12)

- **Source:** branch `feat/model-written-skills`; protocol `docs/model_skills_protocol.md` committed before the run; run commit `9f2974f`.
- **Goal:** does a `SKILL.md` that Qwen2.5-7B writes from its own failure traces raise its strict success on repos it has not seen?
- **Design:** leave-one-family-out (the skill for a family is written only from the other three families' no-skill attempts: 5 failures + 1 success); one skill per family per seed, 20 in all, none leaking an identifier from the repo it is tested on.
- **Run:** `no_skill`, `model_skill`, `handwritten_skills`, `placebo`; 100 tasks × seeds 1–5 = 2,000 runs (job 311230, 2 h 17 min, one RTX 2080 Ti, 0 infrastructure errors). Raw: `runs/model_skills_eval.jsonl`; report `reports/model_skills_eval.md`.
- **Strict success:** no_skill 0.558, model_skill 0.558, handwritten 0.575, placebo 0.537.
- **Primary:** model_skill − no_skill = +0.000, 95% CI [−0.088, +0.097]; 6 better / 8 worse / 5 tied base tasks. Null.
- **Secondary:** model_skill − handwritten −0.017 [−0.105, +0.059]; handwritten − no_skill (5-seed replication) +0.017 [−0.072, +0.114]. Both skill types cut unparseable replies from 24% to 11–12%; placebo did not (31%).
- **Skill content:** generic debugging advice. 0/20 say to keep existing functions/imports when rewriting (6 writer prompts showed an import error after a rewrite); 8/20 advise changing tests, which the agent cannot do.

## What is supported / not supported
- Supported: fixed handwritten skill prompts give no detectable gain on this benchmark for Qwen2.5-7B.
- Supported: in its simplest form (a model-written skill from its own failures), self-improvement gave no detectable gain for Qwen2.5-7B on this benchmark.
- Not supported: any claim of self-improvement, or that RL on this loop would help.
- Limits: held-out tasks share repos with train tasks; the pass-to-pass check is empty for 14 of 19 base tasks; 9 of 19 base tasks tie across all conditions, so power is low.

## Next decisive action
Coordinator decision: either test a stronger skill writer on the same 7B traces (separates writer quality from whether prompt-level skills can help at all), or deprioritize this workstream. RL on this loop is not justified by current evidence.

## Do not overclaim
Two null results on one 7B model and one small benchmark (20 base tasks, held-out sharing repos with train) do not show that skills never help; they show no detectable gain here.
