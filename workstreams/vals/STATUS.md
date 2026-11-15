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
| Results in README / Vals project entry | no |

## Next decisive action
Owner decision needed: harden the tasks (v3: neutral fault messages, no server-side dedup leak) or submit v2 with an honest saturation result.

## Do not overclaim
CI or deterministic integration tests passing is not evidence of frontier-model capability. No results, run IDs or dataset digests exist until Valkyrie reports them. Never modify a task to make a model pass; never commit credentials.

## Evidence handoff
Record run IDs, dataset version/digest, per-task rewards, trace locations and costs here and in `RESULTS.md` when they exist.
