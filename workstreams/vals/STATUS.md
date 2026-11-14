# Vals Benchmaxxing Agent

**Area:** RL Post-Training & Reward Design
**Source:** https://www.vals.ai/hackathon
**Owner agent:** `vals`
**Current agent state:** C++ REWARD ADAPTER IMPLEMENTED, 14/14 CPU TESTS PASSED; NO MODEL/LEADERBOARD RUN

## Research aim
Achieve a measured, reproducible improvement on the **organizer-confirmed Vals Track 2 benchmarks** using a Tinker post-trained model. The approved-attendee Luma listing states **three Vals benchmarks**, while the public Vals website currently specifies a **hidden C++ problem set**; final rules remain in conflict.

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

**Conditional C++ adapter:** Official Tinker Code RL cookbook grades Python, while the public Vals website mentions C++; the approved-attendee Luma description instead specifies three unspecified Vals benchmarks. Implemented a C++17 compile/run adapter, ModalSandboxPool-compatible grading API, and Tinker tool/reward/environment integration wrapping the original RL loop. Tested only the local trusted-code grader and API request shape; real Modal/Tinker integration and official judge compatibility remain unverified.\n\n**Missing access:** Colab CPU previously reported no `TINKER_API_KEY` or Modal tokens in its environment. No assertion about credentials available elsewhere. Public Vals page has not disclosed the official C++ starter, eligible models, training/submission API or scoring protocol.\n\n## Experimental gates
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

## Repo consolidation and official resources — November 13
- Source code is in the existing private `Vedant2100/role-work-forge-artifacts`, isolated at `hackathons/2026-11/vals_tinker/` on branch `agent/vals-tinker/code-rl-preflight`.
- Draft PR (not merged): https://github.com/Vedant2100/role-work-forge-artifacts/pull/2
- Official rules and credit checklist: `hackathons/2026-11/vals_tinker/TRACK_REQUIREMENTS.md`.
- Official Vals FAQ confirms Tinker credits + Modal compute credits and automatic hidden set scoring, but no amounts or redemption details. Organizer email says Slack updates and `$20K` in **prize credits**; not a per-team operating budget.
- Organizers' Luma listing says three Vals benchmarks while current Vals site says C++ hidden set; ask at kickoff which official scoring protocol governs.
- Public materials do not confirm model eligibility, pre-event code rules, scorer API, per-team credits or overage charges.

## Critical scope correction — November 13, 2026
- Directly verified via approved-attendee Luma event details: "Post-Training with Tinker: Post-train a small model and score it on three Vals benchmarks, using Tinker."
- Current vals.ai/hackathon page separately claims a hidden set of C++ competitive-programming problems. The descriptions contradict; **do not treat C++ as the final or sole scoring target**.
- C++17 grader and Tinker adapter remain optional scaffold, with 14 local CPU tests, **not** competition result or proof of relevant training.
- Next step before any training: obtain official names, weights, evaluator starter, model/tool limits for the three Vals benchmarks, and clarify whether the C++ challenge replaces or supplements them.
- Corrected branch README and `TRACK_REQUIREMENTS.md` in the private source repo. Neither event staff nor the current public sources establish a definitive benchmark list yet.
