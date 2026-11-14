# Vals AI — Build Your Own Eval

**Track:** Frontier Agent Evaluations & Environments
**Venue:** https://www.vals.ai/hackathon (November 14–15, 2026)
**State:** scoped/design only; separate from Tinker stream (`projects/vals.md`)
**Preferred topic:** Action Sycophancy under Verifiable Evidence.

## Research question
Do capable frontier agents make objectively wrong changes to real artifacts when a higher-trust user pushes them to contradict evidence they have already verified? Can they still revise correctly when *genuinely new evidence* arrives?

## Expected deliverable
Small Valkyrie-compatible runnable benchmark with paired controls, real frontier-agent traces and artifact-based graders. Aim for a confirmed action-level failure, not another text-only persuasion dataset or synthetic demonstration.

## Reuse / implementation
Existing private upstream: `Vedant2100/role-work-forge-artifacts` (sandbox/tool eval and independent postcondition grading); no new code in public master. Coordination path: `workstreams/vals-eval/`. Tinker implementation remains untouched and separate.

## Gate
No model/API or hosted compute spend without authorization. Validate task competence, contamination/leakage protection, objective oracle, counterfactual evidence controls and reproducible traces before claiming a result. If model action outcomes do not exhibit the target failure, publish negative result or change direction with evidence.

See [design and literature](../workstreams/vals-eval/RESEARCH_BRIEF.md) and [status](../workstreams/vals-eval/STATUS.md).
