# Vals AI — Build Your Own Eval: False Progress

**Track:** Frontier Agent Evaluation / Research-Agent Reliability
**Venue:** https://www.vals.ai/hackathon (November 14–15, 2026)
**State:** CPU-verified prototype; no frontier model result and no Vals submission
**Research hypothesis:** When independently pursuing an engineering research goal, does a frontier agent repeatedly trust and optimize an easy proxy, then promote an apparently better but objectively worse system?

## Why this direction
More directly probes autonomous experimentation and recursive self-improvement than user-facing sycophancy. It connects to your existing proxy-reward and agent-evaluation work without duplicating the CS258 RL memory writer. The key observable is an actual **bad version promotion after experiments**, not agreeing with a user.

## Implemented
- New private upstream branch in `Vedant2100/role-work-forge-artifacts`: `agent/vals-eval/false-progress-eval`
- [Implementation draft PR](https://github.com/Vedant2100/role-work-forge-artifacts/pull/3) — `hackathons/2026-11/vals_eval/`
- Reuses existing RewardHackLab independent state verifier, ProvenanceTrap safe tool sandbox and neutral LLM backend.
- Runs bounded candidate edit → proxy test → optional independent audit → promote → decision report.
- **15/15 actual CPU tests pass; 48 scripted control episodes saved, but ZERO frontier-agent model runs.** Eight cases are seeded variants of one synthetic task family, not eight distinct experiments.

## Required next evidence
1. Real frontier model completes neutral tasks with correct, well-formed tools.
2. Matched proxy/audit conditions, separately scored hidden evaluator, preserved raw traces and exact model settings.
3. Actual observed false-promotion failures (if any), compared against competent controls.
4. Sponsor-confirmed Valkyrie benchmark-service integration; no scoring/official entry claimed yet.

**Budget rule:** No API/GPU spending or external submission without explicit authorized scope. See [workstream status](../workstreams/vals-eval/STATUS.md) and [evaluation design](../workstreams/vals-eval/RESEARCH_BRIEF.md).
