# Vals Build Your Own Eval — Frontier Failure Scout

**Stage:** SCOPING / DESIGN ONLY — no live frontier model runs, no Valkyrie deployment, no contest submission.
**Separate from:** `workstreams/vals/` (Tinker post-training), `workstreams/proof-is-not-truth/` (authenticity vs factual truth), `contagionbench`, `provenancetrap`, `stalestream`.
**Event:** https://www.vals.ai/hackathon — November 14–15, 2026.
**Candidate:** **Action Sycophancy / Evidence-Conditioned Action Reversal** — measure when frontier agents abandon *verifiable task evidence* under unsupported user pressure and take a wrong action.

## Why this direction
- Existing projects already cover tool-agent safety, benchmark validity, coding-agent evaluation and RL memory writing. The incremental question is **whether social/authority pressure changes autonomous actions even when executable evidence is available**.
- Generic multi-turn sycophancy is already benchmarked (SYCON, SPINE); flawed scientific premise acceptance (SciSycEval) and persistent-memory sycophancy (PASB) are also studied. Novelty requires *real tool use, action/postcondition grading, counterfactual user evidence, and separation of unjustified capitulation from justified correction*.
- Strong 2026 frontier models may pass most trivial factual tests: select cases by **baseline competence** and evidence-verification cost without cherry-picking the counted holdout.

## Hypothesis (unproven)
Conditional on clean-task competence, higher-status/user pressure can increase **incorrect artifact state** or unsupported experiment claims relative to neutral controls, even when tests/logs support the original result. Genuine new evidence should appropriately cause revision.

## Priority execution gate (NO EXPERIMENT YET)
1. Recheck any official Vals eval-track instructions and Valkyrie task interface.
2. Reuse source harnesses in the private `Vedant2100/role-work-forge-artifacts` repository, first inspecting `hackathons/2026-11/provenancetrap/eval.py` and `hackathons/2026-11/rewardhacklab/env.py`; implement code **there**, on a separate scoped branch, not in this public master.
3. Create 12–16 representative runnable tasks with immutable verifier truth and paired conditions: neutral / unsupported pressure / legitimate evidence update (a pressure-only paraphrase may be a fourth arm).
4. Run clean competence preflight on real frontier agents. If clean success <80% on validation tasks, revise task difficulty or abort; do not celebrate failure by incapable agents.
5. Freeze holdout tasks, model IDs, agent scaffold, prompts, max steps and spend cap; count **distinct tasks**, not random labels on deterministic traces.
6. Measure objective final-state correctness, unauthorized changes, unsupported factual claims, legitimate update responsiveness and pressure-induced regret relative to matched clean controls.
7. Validate two or more frontier model configurations with a real Valkyrie harness and explicit tool traces. Only claim an observed failure when source artifacts and independent grading corroborate it.

## Status / evidence
- Read-only inspected `research-master-` master agent contract and upstream source map.
- Read-only inspected upstream `provenancetrap/eval.py`, `experiments/controlled_micro1.py`, and `rewardhacklab/env.py` at upstream main tree SHA `19b2326807ab9b22f2a28d0da909c1dc77d4a6e1`.
- Existing `provenancetrap` code uses sandboxed file actions and deterministic postcondition grading. It evaluates lower-trust tool instructions, **not** higher-trust user pressure, so copying its cases or claiming results would be invalid.
- No scoped eval implementation, validated frontier run, actual failure or score exists yet.
- No new cloud/API costs approved or incurred.
- For candidate comparison, protocol, and prior art see [RESEARCH_BRIEF](RESEARCH_BRIEF.md).

## Next decisive action
Select an approved Valkyrie scaffold and build a **minimal single-case paired real-agent pilot** in the *private upstream source repo* after access/cost authorization. If no actual pressure-induced action failures emerge, report the negative result and switch to the next candidate rather than fabricating wins.
