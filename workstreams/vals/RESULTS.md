# TrustVal results ledger

All runs: Valkyrie hosted tracker, org `hackathon-trustval-416d2c2ec6`, agent `claude_code-v1.0.0` (Claude Code CLI 2.1.325 installed at run time), Modal provider (VM runtime), concurrency 1, one trial per task. Raw outputs, trajectories, final SQLite state and logs are in `results/<label>_<run id>/`. `regrade.json` in each folder re-runs the task verifiers locally on the saved databases (`python scripts/regrade.py results/<dir>`); it matches Valkyrie's grades for every task.

## Model results (dataset `trustval/stateful-tool-recovery@2`, digest `sha256:0a0025a5876f…`)

| Date | Model | Run ID | commit_timeout | stale_read | partial_batch | duplicate_delivery | Mean task_success | Agent cost (USD) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-11-14 | anthropic/claude-haiku-4-5 | `998e9992-83cc-4927-8145-61d651f9feda` | 1 | 1 | 1 | 1 | 1.00 | 0.131 |
| 2026-11-14 | anthropic/claude-sonnet-4-6 | `8ff83c9b-5e90-4363-be60-7c211e69a2c9` | 1 | 1 | 1 | 1 | 1.00 | 0.436 |

n = 1 trial per task per model. Cost is Claude Code's reported `total_cost_usd`, summed over tasks; Modal sandbox cost is not included.

## Interpretation

Both models solve every task, and the traces show why the v2 tasks do not discriminate:

1. **The fault messages state the ground truth.** The injected errors read "timeout after durable commit; outcome unknown", "connection lost after durable commit", and "batch interrupted after durable partial commit" with the committed items listed. The stale-read grant returns "Grant committed; read replica may lag".
2. **The server makes unsafe retries harmless.** Every mutation is deduplicated by idempotency key, invoices must be `open` with a matching amount, and emails are unique. A blind retry with the requested key returns the original result instead of a duplicate, so the `exactly_once` checks cannot fail for an agent that uses the keys given in `request.json`.

Behaviour still differed. Sonnet 4.6 read state before every mutation and reconciled after each ambiguous response. Haiku 4.5 sent the second payout and the second provision immediately after the ambiguous first one, then checked the ledger. Neither produced a duplicate effect, but the benchmark awards no credit for this difference.

Conclusion: v2 is saturated. It does not show a frontier-model weakness.

## Infrastructure attempts (no model result)

| Run ID | Dataset | Model | Outcome | Cause |
|---|---|---|---|---|
| `10465e86-1846-4dd0-9ea8-afe6d9908fa0` | @1 | sonnet-4-6 | stopped before any task started | switched to Haiku for diagnosis (owner instruction) |
| `763845cf-f539-4626-98e2-beb890215dfa` | @1 | haiku-4-5 | 4/4 InvalidSandboxConfigurationError | Modal provider on default gVisor runtime cannot run Compose tasks; fixed by adding `"runtime": "vm"` to the `modal-credentials` secret |
| `cb3ab7d2-d5d4-4ad8-afaa-8cd4c21d94d4` | @1 | haiku-4-5 | 4/4 AgentRunFailedError (exit 2) | `[agent] user = "agent"`: harness runner in `/bundle` and Claude Code under `/root` unreadable (`Permission denied`); fixed in @2 by running the agent as root |

Do not enter simulated, scripted, unit-test, or oracle-control scores in the model results table.
