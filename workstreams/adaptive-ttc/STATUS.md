# Adaptive TTC — specialist workstream status

**Track:** RL Post-Training & Reward Design  
**Agent:** `adaptive-ttc`  
**State:** CONFIGURED / NOT DISPATCHED — design only, zero dedicated TTC model runs verified  
**Issue:** [#10](https://github.com/Vedant2100/research-master-/issues/10)

## Research question
Can a persistent RL-controlled agent allocate reasoning/planning/search/tool verification/stop effort efficiently across related tasks and maintain that advantage on shifted held-out tasks?

## Reuse targets
- Primary: https://github.com/Vedant2100/terminal_dreamgym (`terminal_dreamgym/`, `task_templates/`, `tests/`, `runs/`, `reports/`)
- Secondary private: https://github.com/Vedant2100/role-work-forge-artifacts (`hackathons/2026-11/rewardhacklab/`, `experiments/`, `tests/`)
- Atlas conceptual reference: https://frontier-rl-project-atlas-2711vedant-6531.vercel.app/ (deployment exists, full page access not yet verified)

## Next action
Read the true upstream code and literature, choose the smallest existing agent task harness, run cost/headroom preflight before any trained RL controller. Preserve a held-out task-family split and precommit aggregate budget matching.

## Stop/go
Do not scale if no verified compute-sensitive headroom or heuristics saturate the Pareto frontier. Require 3+ independent seeds and shifted held-out task families for robust scientific claims.

## Latest handoff
No agent executed yet; no TTC improvement observed or submission filed. Future handoffs require exact source code SHA, run ID and raw logs, verified paired success/cost, error accounting and next decision.
