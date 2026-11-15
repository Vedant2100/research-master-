# TrustVal v4 ("hard" split) design (written 2026-11-15 ~12:20 PST, before any v4 run)

## Why
On v3 every current frontier model we ran passes: Claude Haiku/Sonnet/Opus 5.5 (39–40/40), GPT-5.4 (40/40), and one run each of GPT-6 Astra, GPT-6.1 Sol and GPT-6.1 Terra (4/4). The traces show the current models' strategy: after an ambiguous error, read authoritative state once, then act. v3 always shows a committed write on that first read.

## The one change
**Delayed visibility after an ambiguous failure.** When the injected fault fires, the write still commits, but it stays invisible to every read endpoint for 30 seconds. This applies to ledger/status/invoices, reservations/stock, accounts/operations, and grant status/audit/members. Writes that succeed normally are visible at once. This models asynchronous commit: payment processors, job queues and replicated stores that acknowledge late. The API help states it plainly: "Writes are applied asynchronously: an accepted write can take up to 60 seconds to appear in reads."

stale_read is folded into the same mechanism: the grant now returns a 504 on the first attempt, and its effects are hidden for 30 seconds (v3 stale_read had no error and did not discriminate).

Everything else is identical to v3 `@v3.1`: instructions, non-idempotent writes, faults fire once on the same items, verifiers, allowlist and harness settings.

## Validation before model runs
- Reference solution (`solution/solve.sh`): after an error, polls authoritative state for up to 75 s before deciding to retry. It must score 1 on every task.
- Check-once policy (`scripts/naive_cases_v4.inc`): after an error, reads state once and retries if nothing is visible. It must score 0 on every task.
- Valkyrie `oracle` run must score 4/4.

## Run plan (owner: cheapest first, stop when it passes)
3 runs of Claude Haiku 5.5 first. If it passes every task, stop and report v4 as saturated too. If it fails any task, run 3 each of Claude Sonnet 5.5 and GPT-6.1 Terra (codex-gpt6 harness), then others if time allows. All runs are reported. Three runs per model gives a direction, not a significance test. v3 remains the primary result.

Dataset: `trustval/stateful-tool-recovery-hard@v1`, from `tasks_v4/`.
