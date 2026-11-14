# Terminal DreamGym Agent

**Area:** Autonomous Research & Self-Improvement
**Source:** https://github.com/Vedant2100/terminal_dreamgym
**Owner agent:** `terminal-dreamgym`
**Current state (2026-11-13):** four preregistered experiments EXECUTED, none shows a gain: handwritten skills (3 seeds, replicated with 5), model-written skills (5 seeds), skills from a 30B writer (5 seeds), and a rerun of handwritten and 30B skills on a new benchmark (v2: 52 calibrated tasks in 16 new repos), where 30B skills showed a small harm. Source changes in terminal_dreamgym PRs [#1](https://github.com/Vedant2100/terminal_dreamgym/pull/1), [#2](https://github.com/Vedant2100/terminal_dreamgym/pull/2), [#3](https://github.com/Vedant2100/terminal_dreamgym/pull/3) and [#4](https://github.com/Vedant2100/terminal_dreamgym/pull/4) (stacked, none merged).

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

## Evidence handoff: skills from a larger writer (2026-11-13)

- **Source:** branch `feat/strong-skill-writer` (PR #3); protocol `docs/strong_writer_protocol.md` committed before any run (`10087df`); run commit `373325f`; results `118d07f`.
- **Goal:** was the model-written null caused by a weak writer? `qwen3-coder:30b` writes the skills from exactly the same Qwen2.5-7B attempts (same selection, prompt, settings); the solver is still Qwen2.5-7B.
- **Run:** `no_skill`, `strong_skill` (30B-written), `model_skill` (unchanged 7B-written skills), `placebo`; 100 tasks × seeds 1–5 = 2,000 runs (job 311752, 2 h 16 min, one RTX 6000 Ada, 0 infrastructure errors). Raw: `runs/strong_writer_eval.jsonl`; report `reports/strong_writer_eval.md`.
- **Strict success:** no_skill 0.568, strong_skill 0.592, model_skill 0.549, placebo 0.571.
- **Primary:** strong_skill − no_skill = +0.023, 95% CI [−0.072, +0.118]; 8 better / 4 worse / 7 tied base tasks. Null.
- **Secondary:** strong_skill − model_skill +0.042 [−0.008, +0.095]; model_skill − no_skill −0.019 [−0.084, +0.055] (replicates the earlier null). 30B skills cut unparseable replies to 6.9% (no skill 23.1%) without raising success. Both skill types raise and lower the same tasks (slug_punctuation 0.44 → 0.92/0.96; sku_preserve_comma 0.84 → 0.56/0.36); placebo does not.
- **Skill content (hand count before results):** 4/20 say to keep existing functions/imports (7B: 0/20); 2/20 advise changing tests (7B: 8/20); 11/20 tell the solver to run tests, which it cannot; 11/20 push `.get()` defaults.
- **Verification:** all 2,000 runs re-scored from saved sandboxes, all match; 0 identifier leaks.
- **Deviation:** first smoke job (2× RTX 2080 Ti) timed out loading the 30B writer and wrote nothing; timeout, warm-up and GPU changed before the counted run (recorded in the protocol).

## Evidence handoff: benchmark v2 (2026-11-13)

- **Source:** branch `feat/benchmark-v2` (PR #4); benchmark and protocol `docs/benchmark_v2_protocol.md` committed before any model run (`98b6e7b`); calibration `c126638`; results `eceb473`.
- **Benchmark:** 16 new small Python repos, 140 injected bugs (one task each), validated so that only the target test fails and at least 3 others pass; trap bugs ship a tempting wrong fix that breaks another test. Repos and bugs written by Claude agents.
- **Calibration:** no_skill, seeds 101–105, 700 runs (job 311913). Preregistered keep rule (solved 1–4 of 5): 52 of 140 kept, all 16 repos.
- **Run:** `no_skill`, `handwritten_skills`, `strong_skill` (qwen3-coder:30b, written from 7B failures on the *original* repos, one per seed), `placebo`; 52 tasks × seeds 1–5 = 1,040 runs (job 312042, 2 h 48 min, 0 infrastructure errors). Strict success 0.488 / 0.454 / 0.389 / 0.423.
- **Co-primary (97.5%, repo-cluster bootstrap):** handwritten − no_skill −0.035 [−0.129, +0.053], null; strong − no_skill −0.100 [−0.187, −0.018], harm by the preregistered rule, negative on all 5 seeds.
- **Secondary:** placebo − no_skill −0.065 [−0.157, +0.033]; strong − placebo −0.035 [−0.162, +0.073]. The harm cannot be separated from an effect of extra prompt text.
- **Verification:** all 1,040 runs re-scored from saved sandboxes, all match. Re-scoring script changed after the run (tasks-file argument, timeout counted as failure); recorded as a deviation.
- **Limit:** v2 fixes validity (new repos, non-empty pass-to-pass, no all-tie tasks) but intervals are about as wide as before (±0.09).

## What is supported / not supported
- Supported: fixed handwritten skill prompts give no detectable gain on this benchmark for Qwen2.5-7B.
- Supported: in its simplest form (a model-written skill from its own failures), self-improvement gave no detectable gain for Qwen2.5-7B on this benchmark.
- Supported: a stronger writer (30B) on the same failures also gave no detectable gain, so the null is not explained by the 7B writer alone.
- Supported: on new repos (v2), handwritten skills gave no detectable gain, and 30B skills learnt on other repos lowered strict success slightly (−0.100); a placebo also scored lower, so the cause may be extra prompt text.
- Not supported: any claim of self-improvement, or that RL on this loop would help.
- Limits (original benchmark): held-out tasks share repos with train tasks; the pass-to-pass check is empty for 14 of 19 base tasks; 9 of 19 base tasks tie across all conditions. v2 removes these but is no more precise (±0.09).

## Next decisive action
Recommendation for the coordinator: deprioritize this workstream. Four experiments found no gain from prompt-level skills on a 7B solver, on the original repos or new ones. If it continues, the cheapest informative step is separating extra-text effects from skill content (several placebo lengths), or skills written from failures on the same v2 repos. RL on this loop is not justified by current evidence.

## Do not overclaim
Four results on one 7B solver and two small benchmarks do not show that skills never help; they show no detectable gain here, with intervals of about ±0.09. The v2 harm is one comparison and is confounded with prompt length.
