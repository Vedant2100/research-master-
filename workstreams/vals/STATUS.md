# Vals Benchmaxxing Agent

**Area:** RL Post-Training & Reward Design
**Source:** https://www.vals.ai/hackathon
**Owner agent:** `vals`
**Current agent state:** CPU PREFLIGHT EXECUTED (7/7 TESTS + C++ COMPILE SMOKE); NO MODEL/LEADERBOARD RUN

## Research aim
Achieve a measured, reproducible score improvement on the official hidden C++ code-solving benchmark using a Tinker post-trained model.

## Current source and workstream isolation
- **Upstream private source:** `Vedant2100/role-work-forge-artifacts`
- **Isolated source branch:** `agent/vals-tinker/code-rl-preflight`
- **Preflight files:** `hackathons/2026-11/vals_tinker/{README.md,preflight.py,tests/test_preflight.py}`
- **Master coordination branch:** `agent/vals/tinker-preflight`
- **Reference recipe:** https://tinker-docs.thinkingmachines.ai/cookbook/recipes/code-rl/

## Implemented (not executed as model training)
- Read event page; hidden C++ evaluation on live leaderboard, official Tinker and Modal credits.
- Inspected actual upstream RewardHackLab code and confirmed ticket-agent verifier cannot act as C++ code judge.
- Scoped distinct workstream, using official cookbook rather than copying or building a Tinker trainer.
- Added print-only training command, environment metadata preflight, train-only sample-difficulty diagnostics, and seven regression tests; all 7 passed on a Colab CPU runtime. Local g++ 13.3.0 compiled and ran a trivial C++17 sum program successfully.
- **Colab access restored:** account reconnected; CPU-only preflight completed, no GPU used.
- No paid compute, API calls, model weights, official evaluator access, hidden samples, training checkpoints, or competition submissions. 

**Critical compatibility gap:** official Tinker Code RL cookbook grades **Python** (`code.py`, `python run.py`, Python-specific tool descriptions), whereas Vals requires **C++**. The cookbook training command cannot be treated as an official Vals C++ pipeline. Obtain official starter/judge and adapt compile/execute/reward handling before any genuine training.\n\n**Missing access:** Colab CPU reported no `TINKER_API_KEY` or Modal tokens in its environment. No assertion about credentials available elsewhere.\n\n## Experimental gates
1. Kickoff: confirm organizer-allowed models/data, exact C++ tool use, hidden test scoring, inference and checkpoint submission rules.
2. Establish actual official baseline before training; preserve raw scoring output.
3. After authorization and environment access, run a tiny genuine training smoke using upstream Tinker Code RL recipe and approved sandbox.
4. Train/checkpoint/validate with train-only difficulty selection and an independent local held-out split.
5. Report baseline → trained score, total training steps, model/checkpoint URI, actual credits, fair inference budget and receipt. No proxy claims.

## Open approvals / blockers
- Reconnect Google authorization for Colab runtime.
- Confirm availability of Tinker credentials/event credits and Modal sandbox credentials at kickoff.
- User approval required before paid compute or external leaderboard submission.

## Evidence handoff
**Stage:** preparation. No model outcome, official benchmark score, or submission. Do not mislabel source/test existence as execution.
