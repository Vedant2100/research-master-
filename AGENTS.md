# Master agent contract

**Four active research tracks; nine thread-specific specialists.** Each role owns one research question and one status file. This repo tracks evidence and coordination; code and raw results remain in their original repositories.

## Mandatory upstream reuse (supersedes any suggestion to reimplement)

Before writing code, every specialist MUST open [SOURCE_MAP.md](SOURCE_MAP.md), access the correct original upstream repository and any relevant experiment branches, inspect existing source/tests/configs/results, and continue the implementation from there. **Do not create duplicate harnesses, experiment pipelines, training code, or source copies in this master.** Only missing functionality is implemented, as scoped changes to the original upstream source. Vals reuses RewardHackLab/evaluation infrastructure; Iterate reuses Terminal DreamGym. If the original repo is private or unavailable, stop and report access needs, not an invented substitute.

## Workflow
1. Read `README.md`, `AGENT_ROSTER.md`, `GOVERNANCE.md`, `EVIDENCE.md`, the assigned `projects/<slug>.md`, its `workstreams/<slug>/STATUS.md`, and the actual source repository.
2. Record hypothesis, controls, split, seeds, worker, verifier SHA, cost cap and end-to-end timing before a new experiment.
3. Confirm source-repo access and resource budget. **Never launch GPU/cloud/API workloads or submit external forms without explicit authorization.**
4. If access is limited to this repository, update only the assigned status and create actionable, precise source-repo change proposals; do not pretend to have run code elsewhere.
5. Keep separate **designed / implemented / executed / replicated / submitted / accepted**. CI green is never evidence of a successful model run. Don't conflate SFT with GRPO, UCB with actor-critic, or deterministic replay seeds with independent trials.
6. Use a branch `agent/<slug>/<task>` and a scoped PR. Allowed paths are `workstreams/<slug>/**` and (with source evidence) `projects/<slug>.md`; shared file changes require explicit coordinator review.
7. Record exact source SHA, commands, task/seed counts, raw result URL, failure modes, budget spent, next decision and human approvals using `templates/EXPERIMENT_HANDOFF.md`.
8. Do not edit or close another agent's issue or source code; do not merge your own PR. The coordinator reviews cross-track collisions.
9. This repo is **public**. Do not post API tokens, private source code, confidential data, personal application details or cluster credentials.
10. Preserve negative results, causal limitations, preregistrations and venue submission receipts. If blocked, report rather than silently substituting a different experiment.

## Invocation
- GitHub Copilot: one agent profile at `.github/agents/<slug>.agent.md` per workstream; select with supported Copilot interface. Profiles do not start jobs by themselves.
- Codex: one project-scoped role at `.codex/agents/<slug>.toml`; explicitly delegate from a session with the necessary repo permissions.
- Parallelism is permitted only when resources and assignments are independently isolated. Never invent agent sessions, submissions or model runs.

Supporting Fleet-Mem governance is prior work, **not a tenth agent**.
