# Source map — canonical code and evidence locations

> **Portfolio rule (2026-11-16):** this public repository is the coordination and evidence-summary control plane. Canonical experiment code and raw results remain in their source repositories unless an explicit owner decision says otherwise. Workstream status summaries live under `workstreams/<slug>/`; do not import whole repositories or private code into this public repository.

**Use existing code, configs, tests, artifacts and results first.** This repository is not a replacement monorepo or a synchronization system. Never copy private code, test fixtures, credentials, raw conversations or private artifacts into the public master.

## Exact source locations

| Agent | Canonical repository / branch | Read existing code and evidence FIRST |
|---|---|---|
| `frontiermemory` | Experiments: [Vedant2100/frontiermemory-learning](https://github.com/Vedant2100/frontiermemory-learning) `main`; submitted paper: [Vedant2100/frontiermemory-forge-repo](https://github.com/Vedant2100/frontiermemory-forge-repo) | Experiment `FINAL-RESULTS.md`, `STATUS-DETAILED.md`, `results/official/`; paper repository and FORGE submission record. |
| `evomembench` | [Vedant2100/evo-mem-bench](https://github.com/Vedant2100/evo-mem-bench) `main`; also inspect `codex/full-memory-arm-matrix` | `src/`, `scripts/`, `configs/`, `docs/`, `tests/`, `reports/`; compare the full-arm branch before choosing methods. |
| `stalestream` | [Vedant2100/f26](https://github.com/Vedant2100/f26) `main` **private** | `cs258/stalestream/RESEARCH_MATURATION_2026-11-10.md`, `headroom_gate.py`, and the current CS258 proposal/design assets. Writer/training implementation is not yet verified. |
| `contagionbench` | [Vedant2100/role-work-forge-artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) `main` **private** | `hackathons/2026-11/contagionbench/`, `experiments/swarm_v3.py`, `experiments/swarm_repro.py`, control preflight, reports and raw results. |
| `provenancetrap` | Same private [role-work-forge-artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) `main` | `hackathons/2026-11/provenancetrap/`, evaluation scripts, controlled experiments, reports and raw traces. |
| `rewardhacklab` | Same private [role-work-forge-artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) `main` | `hackathons/2026-11/rewardhacklab/`, Modal runner, SFT/RL scripts, `results/`; corrected SFT run 43647115920 and interrupted GRPO run 43641448741. |
| `vals` | [Vedant2100/trustval](https://github.com/Vedant2100/trustval) `main` — canonical since 2026-11-15 | `README.md`, `RESULTS.md`, `DESIGN_V3.md`, task manifests and raw `results/`. The copy in `workstreams/vals/` is a frozen historical snapshot; do not revive it. |
| `terminal-dreamgym` | [Vedant2100/terminal_dreamgym](https://github.com/Vedant2100/terminal_dreamgym) `main` | `terminal_dreamgym/`, `task_templates/`, `curricula/`, `skills/`, `tests/`, `runs/`, `reports/`. This workstream is deprioritized; no further runs are planned. |
| `iterate` | Event declined; historical work reused [Vedant2100/terminal_dreamgym](https://github.com/Vedant2100/terminal_dreamgym) | Retain the event record only. Do not open a new event stream or duplicate DreamGym code. |
| `adaptive-ttc` | Reuse [Terminal DreamGym](https://github.com/Vedant2100/terminal_dreamgym) and, if needed, private [Role Work Forge artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) | Inspect existing verifiable tasks and cost traces first. The Atlas is a conceptual reference, not a verified code source. |

## Mandatory agent bootstrap

1. Identify the assigned active workstream via `AGENT_ROSTER.md` and locate its canonical source above.
2. Read current source branches, tests, configs and raw evidence. Pin the exact commit SHA and branch in the handoff.
3. Run existing CPU/unit/smoke checks in an authorized environment. A green CI result is not model-performance evidence.
4. Reuse the real entry point. Make code changes in the canonical source repository on a scoped branch, not in this control-plane repository.
5. Report exact source commits, commands, run IDs, per-episode evidence, matched comparisons, costs, caveats and blockers in the corresponding master status file.
6. For shared source code (ContagionBench/ProvenanceTrap/RewardHackLab or DreamGym/TTC), use distinct branches and coordinate changes.
7. New GPU/API spend, external submission or work affecting third parties requires explicit user authorization. Preserve existing approved limits.
8. Do not expose private source code, raw private artifacts, secrets or personal data in this public repository.

## Scope control

This map is an index, not a synchronization system. No Git submodules, wholesale source copies, new scientific CI runners or auto-launched agents are needed. First establish what exists, which version works and the smallest justified next change.
