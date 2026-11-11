# Canonical upstream code map — reuse before implementation

**All ten specialists must use existing working code, configs, tests, artifacts, and prior experiment results. This public master is a control plane, not a monorepo. Do not copy source directories or rebuild a working harness here.**

## Exact source locations

| Agent | Repository / branch | Read existing code and evidence FIRST |
|---|---|---|
| `frontiermemory` | [Vedant2100/frontiermemory-learning](https://github.com/Vedant2100/frontiermemory-learning) `main` | `official/`, `scripts/`, `configs/`, `paper/`, `results/official/`, `STATUS-DETAILED.md` |
| `evomembench` | [Vedant2100/evo-mem-bench](https://github.com/Vedant2100/evo-mem-bench) `main`, also inspect `codex/full-memory-arm-matrix` | `src/`, `scripts/`, `configs/`, `docs/`, `tests/`, `reports/`; full-arm branch may contain methods absent from `main`. Compare branches before choosing. |
| `stalestream` | [Vedant2100/f26](https://github.com/Vedant2100/f26) `main` **private** | `cs258/stalestream/RESEARCH_MATURATION_2026-11-10.md`, `cs258/stalestream/headroom_gate.py`, existing CS258 proposal assets. **Writer/training implementation does not yet exist**; build only genuinely missing components. |
| `contagionbench` | [Vedant2100/role-work-forge-artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) `main` **private** | `hackathons/2026-11/contagionbench/experiment.py`, `experiments/swarm_v3.py`, `experiments/swarm_repro.py`, `experiments/swarm_all_defenses_control_preflight.py`, `results/`, `reports/`, `tests/`. All experiment paths relative to `hackathons/2026-11/`. |
| `provenancetrap` | Same private [role-work-forge-artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) `main` | `hackathons/2026-11/provenancetrap/eval.py`, `experiments/micro1_repro.py`, `experiments/micro1_v3.py`, `experiments/controlled_micro1.py`, `results/`, `reports/`, `tests/`. |
| `rewardhacklab` | Same private [role-work-forge-artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) `main` | `hackathons/2026-11/rewardhacklab/env.py`, `agenttune_smoke.py`, `experiments/lexsi_train_cohere.py`, `experiments/lexsi_repro.py`, `experiments/ticket_model_eval.py`, `modal/`, `results/`; existing [HF Tiny Aya adapter](https://huggingface.co/Artemis2100/rewardhacklab-tiny-aya-global-lexsi-2026). |
| `vals` | **Event workstream, no separate code repository** | Reuse relevant existing post-training/evaluation infrastructure from `role-work-forge-artifacts/hackathons/2026-11/` and `rewardhacklab`, then official Vals benchmark SDK/evaluator if released. Never invent a proprietary/official benchmark. Coordinate code changes with `rewardhacklab`. |
| `terminal-dreamgym` | [Vedant2100/terminal_dreamgym](https://github.com/Vedant2100/terminal_dreamgym) `main` | `terminal_dreamgym/`, `task_templates/`, `curricula/`, `skills/`, `tests/`, `runs/`, `reports/live_model_run_qwen.md`, `reports/report.md`; investigate conflicting pilot/sweep results before new implementation. |
| `iterate` | **Event workstream, reuses** [Vedant2100/terminal_dreamgym](https://github.com/Vedant2100/terminal_dreamgym) | Use the same DreamGym run/eval/skill-promotion code and existing demo, adding only event-specific integration if needed. Coordinate shared source changes with `terminal-dreamgym`; no duplicate self-improvement engine. |

## Mandatory agent bootstrap

1. Identify the assigned slug via `AGENT_ROSTER.md` and locate its upstream above. Obtain **read access** through an available GitHub connection, clone, or existing workspace checkout. If private repo access is missing, report the blocker; don't invent code.
2. Read the *current upstream main branch*, relevant experimental branches, upstream `README`, existing tests, configs and raw evidence. Pin the exact commit SHA and document the branch.
3. Execute existing CPU/unit/smoke checks in a safe authorized environment. Examine actual previous run files and logs. **Never assume a green CI result proves model performance.**
4. Find and reuse the real entry point. If functionality is absent, extend **that upstream repository** on a scoped branch, not the master. Reuse existing helper modules, evaluators, manifests, logging and adapters. Do not introduce a second framework unless a concrete deficiency is demonstrated.
5. Report code changes and experimental result links back to `workstreams/<slug>/STATUS.md`; use an upstream PR for code changes and a master PR for status. Track upstream SHA, tests, execution provenance and source of truth.
6. When two agents share upstream code (safety trio, RewardHackLab/Vals, DreamGym/Iterate), use distinct branches and never alter another lane without explicit coordination.
7. Source reads alone are fine; **new GPU/API spend, external paper/event submission or work affecting third parties still requires explicit user authorization**. If the user has already authorized a specific run, preserve its exact limits.
8. Do not mirror **private** upstream code, test fixtures, secrets, private artifacts, or personally identifying files into this **public** master. An agent may summarize findings and link to private refs without exposing their contents.

## Scope control

This map is an index, not a synchronization system. No Git submodules, copies of entire repos, new CI runners for the scientific workloads, or auto-launched agents are needed. Each specialist should first answer: **What already exists, which version works, and what is the smallest justified next change?**


## New tenth agent — Adaptive TTC (conditional pilot)

| Agent | Existing sources (do not duplicate) | First verified scope |
|---|---|---|
| `adaptive-ttc` | [Terminal DreamGym](https://github.com/Vedant2100/terminal_dreamgym) `main` — `terminal_dreamgym/`, `task_templates/`, `tests/`, `runs/`, `reports/`; [private Role Work Forge artifacts](https://github.com/Vedant2100/role-work-forge-artifacts) `main` — `hackathons/2026-11/rewardhacklab/`, `experiments/`, `tests/`; [Frontier Agent Learning Atlas](https://frontier-rl-project-atlas-2711vedant-6531.vercel.app/) as conceptual design artifact, **not code verified available**. | Read original repos and tests first, choose a verifiable task harness with measurable compute sensitivity, then implement only the missing TTC action-router module **in that source repository**. Coordinate with `terminal-dreamgym` and `rewardhacklab`; do not copy their code into this public master. |

The Vercel Atlas deployment exists and is READY but its deployment file-reader truncates the HTML. Do not claim a full Atlas audit until an authorized full-page read is available.
