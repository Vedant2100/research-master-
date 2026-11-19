# Delivery plan (America/Los_Angeles)

**2026-11-16 reconciliation:** Nov 12–15 items below are historical, not pending deliverables. FrontierMemory paper and DreamGym research are complete; TrustVal benchmark evaluation is complete but official event submission is unverified; RewardHackLab corrected SFT gate passed but its RL comparison remains.

| Date | Work |
|---|---|
| Nov 12 | StaleStream proposal (target, check Canvas) |
| Nov 13 | AGENTVERIFY eligibility/abstract gate check |
| Nov 14–15 | Vals approved sprint; Iterate if registration verified, overlaps |
| Nov 15 AoE | FORGE FrontierMemory audited paper; Lexsi Stage 1 RewardHackLab (11:59 PM AoE) |
| Nov 19 | StaleStream oracle >=90%, >=20 pt headroom, 300 frozen episodes and timed 20-step GRPO gate |
| Nov 20 | AGENT 2027 short/full paper candidate only with mature safety or DreamGym evidence |
| Nov 24 | StaleStream controller + 100-step GRPO pilot decision |
| Dec 3 | StaleStream result freeze |
| Dec 10 | StaleStream final report/code |
| Dec 11–13 | Apart Agent Attribution sprint only if registered, new attribution experiments |

**Next live decisions:** Nov 19 StaleStream oracle/headroom/300-episode/timing gate; Nov 20 safety paper only with real causal replication; Nov 24 StaleStream GRPO pilot; RewardHackLab matched proxy-vs-verified RL pilot using the competent SFT adapter; EvoMemBench ALFWorld lifecycle repair + matched competence. Preserve explicit stage/receipt distinctions.

**Weekly minimum:** Report blocker, evidence URL and next decisive action only for unfinished funded workstreams. Do not create repeat experiments just to fill an area after DreamGym or TrustVal has completed.

## TTC incubation — internal checkpoints, not external deadlines
- First: inspect the entire accessible [Atlas](https://frontier-rl-project-atlas-2711vedant-6531.vercel.app/) and existing DreamGym/RewardHackLab source + actual traces; write a prior-art overlap matrix against learned dynamic planning and reasoning-budget papers.
- Then: run cheap paired task-level headroom assessment (fixed low/high budget and strongest cheap heuristic), recording real tokens, latency, verification/tool calls and terminal success. Coordinate with source-repo owners; do not duplicate a harness.
- Only if competence, budget sensitivity and heldout splits are verified: implement an actual experience-adaptive RL allocation policy, compare vs heuristics/bandits/SFT router, replicate across >=3 independent seeds and shifted task families.
- Go/no-go before any material GPU allocation; this remains a **conditional tenth workstream** within the existing four active tracks, not a fifth track or confirmed TTC result.
