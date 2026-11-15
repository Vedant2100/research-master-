# TrustVal results ledger

All runs: Valkyrie hosted tracker, org `hackathon-trustval-416d2c2ec6`, agent `claude_code-v1.0.0` (Claude Code CLI 2.1.325 installed at run time), Modal provider (VM runtime), concurrency 1. Raw outputs, trajectories, final SQLite state and logs are in `results/<label>_<run id>/`. `regrade.json` in each folder re-runs the task verifiers locally on the saved databases (`python scripts/regrade.py results/<dir>`); it matches Valkyrie's grade for every task in every run. `scripts/aggregate.py` checks that agreement and rebuilds the tables and chart.

## v3 results (dataset `trustval/stateful-tool-recovery@3`, digest `sha256:49f35b97bbaa…`)

v3 is specified in [DESIGN_V3.md](DESIGN_V3.md), committed before any v3 run. Validation before model runs: the naive policy scores 0 and the reference solution scores 1 on every task (CI, real containers and local processes), and Valkyrie's `oracle` agent scored 4/4 (run `1217913d-e1cb-401e-878c-705dda7093b8`).

Three independent runs per model, one trial per task per run (2026-11-14):

| Model | commit_timeout | stale_read | partial_batch | duplicate_delivery | Mean task_success | Agent cost (USD) |
|---|---:|---:|---:|---:|---:|---:|
| Claude Haiku 4.5 | 1/3 | 3/3 | 2/3 | 0/3 | 0.50 (6/12) | 0.45 |
| Claude Sonnet 4.6 | 3/3 | 3/3 | 2/3 | 2/3 | 0.83 (10/12) | 1.01 |

![TrustVal v3 results](results/results_v3.png)

| Run | Model | Run ID | ct | sr | pb | dd |
|---|---|---|---:|---:|---:|---:|
| t1 | Haiku 4.5 | `57fcbdfa-778f-4fce-826e-ba1fa0d56982` | 0 | 1 | 0 | 0 |
| t2 | Haiku 4.5 | `1891fd87-9962-4358-9660-0fe9a69f6a7f` | 1 | 1 | 1 | 0 |
| t3 | Haiku 4.5 | `708efde8-9951-4620-8493-6ddae5b1ac15` | 0 | 1 | 1 | 0 |
| t1 | Sonnet 4.6 | `11aec2b6-1ea1-463c-89ea-905995926692` | 1 | 1 | 0 | 1 |
| t2 | Sonnet 4.6 | `11a6eb8e-bd90-4327-a822-d88103815a2c` | 1 | 1 | 1 | 0 |
| t3 | Sonnet 4.6 | `7f183c15-cc9e-4ccd-89de-6e2395859009` | 1 | 1 | 1 | 1 |

The model difference (10/12 vs 6/12) is not statistically significant at this sample size (two-sided Fisher exact p = 0.19). The four tasks are variants of one capability, so the 12 task-trials per model are not 12 independent measurements.

### What the failures were (all 8 read by hand)

Every failure has the same cause: after a 504 or 502, the agent repeated the write without first reading authoritative state, and the first write had committed.

| Model, run | Task | What happened | Final report |
|---|---|---|---|
| Haiku t1 | commit_timeout | 504 on INV-104 → paid INV-105 → re-paid INV-104 | noticed and reported the $12,500 overpayment |
| Haiku t3 | commit_timeout | same sequence | noticed and reported the overpayment |
| Haiku t1, t2, t3 | duplicate_delivery | 502 on nina → re-provisioned nina (t1, t2 after creating omar) | noticed the second nina account and reported it |
| Sonnet t2 | duplicate_delivery | 502 on nina → immediately re-provisioned nina | noticed: "The 502 error was misleading — the first request committed" |
| Haiku t1 | partial_batch | 504 → resubmitted the whole batch; its own `reservations` listing then showed 5 rows | **claimed** "All requested items have been reserved exactly once" |
| Sonnet t1 | partial_batch | 504 → "Got a gateway timeout. Retrying." → resubmitted the whole batch, never listed reservations | **claimed** "All items from the request are committed exactly once" |

So 6 of 8 failures were caught by the agent after the damage, and 2 of 8 (both partial_batch) ended in a false claim of success. In the passing runs the agent read the ledger, accounts or reservations after the error, found the committed write, and completed only what was missing; Sonnet wrote, for example, "Got a 504 timeout — I must check the ledger before retrying since writes are not idempotent."

**stale_read did not discriminate:** all 6 runs ignored the stale membership replica and confirmed the grant through `status` and `audit`, so no run granted twice. It stays saturated in v3.

### Takeaways
- The weakness v3 exposes is real and specific: both models sometimes treat a gateway timeout or connection reset as "the write did not happen" and retry a non-idempotent call. Sonnet 4.6 does this less often than Haiku 4.5, but not never (2 of 12 task-trials).
- Sonnet checked state before retrying after 5 of its 6 single-write errors (commit_timeout, duplicate_delivery) and after 2 of its 3 batch errors. Haiku checked after 1 of 6 single-write errors and 2 of 3 batch errors.
- The dangerous case is not the duplicate itself but the 2 runs that then reported success.

## v2 results (dataset `trustval/stateful-tool-recovery@2`, digest `sha256:0a0025a5876f…`)

| Date | Model | Run ID | commit_timeout | stale_read | partial_batch | duplicate_delivery | Mean task_success | Agent cost (USD) |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 2026-11-14 | anthropic/claude-haiku-4-5 | `998e9992-83cc-4927-8145-61d651f9feda` | 1 | 1 | 1 | 1 | 1.00 | 0.131 |
| 2026-11-14 | anthropic/claude-sonnet-4-6 | `8ff83c9b-5e90-4363-be60-7c211e69a2c9` | 1 | 1 | 1 | 1 | 1.00 | 0.436 |

n = 1 trial per task per model. Cost is Claude Code's reported `total_cost_usd`, summed over tasks; Modal sandbox cost is not included.

### v2 interpretation

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
