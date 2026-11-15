# TrustVal (Vals AI Build Your Own Eval)

**Area:** RL Post-Training & Reward Design (evaluation lane)
**Event:** Vals AI hackathon, Build Your Own Eval track, Nov 14–15 2026 (https://www.vals.ai/hackathon)
**Vals org:** `hackathon-trustval-416d2c2ec6`
**Owner agent:** `vals`
**Dataset:** `trustval/stateful-tool-recovery@v1` (4 Harbor tasks)

## Canonical source

As of 2026-11-14 the TrustVal implementation lives **in this directory** (`workstreams/vals/`) and all further work happens here. It was imported from `Vedant2100/role-work-forge-artifacts` `main` @ `be8f2eb` (PR #4, `hackathons/2026-11/trustval/`), byte-identical at import. That copy is frozen history; do not edit it or revive the discarded earlier implementation. The earlier "Vals Benchmaxxing" plan (baseline → training → eval) is superseded.

## Layout
- `README.md`: benchmark description, setup, run commands
- `RESULTS.md`: results ledger (no model results yet)
- `tasks/{commit_timeout,stale_read,partial_batch,duplicate_delivery}/`: Harbor tasks
- `scripts/`: `smoke_test.sh` (structure), `write_manifest.py` (generates `tasks/dataset.toml`, not committed), `compose_smoke_test.sh` (Docker API + verifier exercise)
- CI: `.github/workflows/trustval-validation.yml`

## State (designed / implemented / executed / replicated / submitted)
| Stage | Status |
|---|---|
| Designed | yes |
| Implemented (4 tasks, hidden-state verifiers) | yes |
| Structure smoke test | passes locally at import (2026-11-14) |
| Docker build + compose smoke test in CI | passes (research-master- PR #14, run 43659141063) |
| `harbor lint` (harbor 0.26.0, Compose v5.7.1) | clean on all 4 tasks (2026-11-14) |
| Dataset pushed to Valkyrie | yes: `trustval/stateful-tool-recovery@1` (tags `v1`, `latest`), digest `sha256:fcba126ca3b849c759e1b88c971fd03a65a4cd908abb994d1ff13f7011df48eb`, 4 tasks, pushed 2026-11-14 16:52 PST from research-master `db71688`; per-task digests match `scripts/write_manifest.py` |
| Agent installed | `claude_code-v1.0.0` from vals-ai/public-agent-registry `examples/claude_code-v1.0.0` |
| Dataset v2 | `trustval/stateful-tool-recovery@2` (tags `v2`, `latest`), digest `sha256:0a0025a5876f…`: agent user `agent` → `root` (harness compatibility; see RESULTS.md) |
| Model runs | Haiku 4.5 `998e9992…` 4/4; Sonnet 4.6 `8ff83c9b…` 4/4 (1 trial/task); locally re-graded, matches |
| Finding | v2 saturated: fault messages reveal outcome and server dedup makes blind retries safe |
| v3 design | `DESIGN_V3.md`, committed (`2116af2`) before any v3 run |
| v3 validation | naive policy 0 / reference solution 1 on all tasks (CI containers + local); Valkyrie oracle 4/4 (`1217913d…`) |
| Dataset v3 | `trustval/stateful-tool-recovery@3` (tags `v3`, `latest`), digest `sha256:49f35b97bbaa6a22810c24232ea9c7532151b454b59be345d1c0defdd075063b` |
| v3 model runs | 3 runs × 4 tasks per model. Haiku 4.5: 6/12 (ct 1/3, sr 3/3, pb 2/3, dd 0/3). Sonnet 4.6: 10/12 (ct 3/3, sr 3/3, pb 2/3, dd 2/3). Fisher p = 0.19. All 8 failures: blind retry of a committed non-idempotent write; 2 ended in a false success claim. Re-graded locally, matches Valkyrie |
| Spend | about $2.03 Claude Code reported cost across all runs (v2 $0.57, v3 $1.46), plus Modal sandbox time on workspace `artemis-76548` |
| Results in README / Vals project entry | no |

## Next decisive action
Owner: write the one-paragraph human overview for the README, review PRs #15/#16, and fill the Vals project entry (name, description, repo link). Optional: more runs per model to tighten the Haiku/Sonnet comparison; replace or harden stale_read (saturated in v3).

## Do not overclaim
CI or deterministic integration tests passing is not evidence of frontier-model capability. No results, run IDs or dataset digests exist until Valkyrie reports them. Never modify a task to make a model pass; never commit credentials.

## Evidence handoff
Record run IDs, dataset version/digest, per-task rewards, trace locations and costs here and in `RESULTS.md` when they exist.
