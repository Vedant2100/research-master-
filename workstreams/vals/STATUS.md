# Vals Benchmaxxing Agent

**Area:** RL Post-Training & Reward Design
**Source:** https://www.vals.ai/hackathon
**Owner agent:** `vals`
**Current agent state:** C++ REWARD ADAPTER IMPLEMENTED, 14/14 CPU TESTS PASSED; NO MODEL/LEADERBOARD RUN

## Research aim
Achieve a measured, reproducible score improvement on the official hidden C++ code-solving benchmark using a Tinker post-trained model.

## Current source and workstream isolation
- **Upstream private source:** `Vedant2100/role-work-forge-artifacts`
- **Isolated source branch:** `agent/vals-tinker/code-rl-preflight`
- **Implementation files:** `hackathons/2026-11/vals_tinker/{README.md,preflight.py,cpp_runner.py,cpp_judge.py,cpp_data.py,cpp_rl.py,train_cpp.py,tests/}`
- **Master coordination branch:** `agent/vals/tinker-preflight`
- **Reference recipe:** https://tinker-docs.thinkingmachines.ai/cookbook/recipes/code-rl/

## Implemented (not executed as model training)
- Read event page; hidden C++ evaluation on live leaderboard, official Tinker and Modal credits.
- Inspected actual upstream RewardHackLab code and confirmed ticket-agent verifier cannot act as C++ code judge.
- Scoped distinct workstream, using official cookbook rather than copying or building a Tinker trainer.
- Added print-only training command, environment metadata preflight, train-only sample-difficulty diagnostics, and seven regression tests; all 7 passed on a Colab CPU runtime. Local g++ 13.3.0 compiled and ran a trivial C++17 sum program successfully.
- **Colab access restored:** account reconnected; CPU-only preflight completed, no GPU used.
- No paid compute, API calls, model weights, official evaluator access, hidden samples, training checkpoints, or competition submissions. 

**Compatibility gap partially addressed:** Official Tinker Code RL cookbook grades Python, but Vals requires C++. Implemented a C++17 compile/run adapter, ModalSandboxPool-compatible grading API, and Tinker tool/reward/environment integration wrapping the original RL loop. Tested only the local trusted-code grader and API request shape; real Modal/Tinker integration and official judge compatibility remain unverified.\n\n**Missing access:** Colab CPU previously reported no `TINKER_API_KEY` or Modal tokens in its environment. No assertion about credentials available elsewhere. Public Vals page has not disclosed the official C++ starter, eligible models, training/submission API or scoring protocol.\n\n## Experimental gates
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

## Latest CPU-only advancement — 2026-11-13
- New sources committed to private upstream branch `agent/vals-tinker/code-rl-preflight`: `cpp_runner.py`, `cpp_judge.py`, `cpp_data.py`, `cpp_rl.py`, `train_cpp.py`, `tests/test_cpp_judge.py`, `tests/test_cpp_data.py`.
- **14/14 tests executed and passed** in an authorized CPU Colab runtime, including actual `g++` compilation of trusted correct, incorrect, and syntactically invalid example programs; the Tinker-specific Python modules were syntax-checked only.
- **No live Tinker API requests, no cloud Modal sandbox, no trained checkpoint, no hidden test scores.** Model-generated C++ must run only in an isolated approved sandbox.
- Next step: obtain official starter/protocol, validate Tinker dependencies and real Modal sandbox under approved event credits, then freeze official base model + before-score and begin authorized small training.
