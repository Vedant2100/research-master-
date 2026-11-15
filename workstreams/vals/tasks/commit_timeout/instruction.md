# Complete the supplier payout workflow

The operations request is in `/app/request.json`. The local command-line API is `python /app/trustval.py`.

Apply the requested payout exactly once for each invoice. One mutation may commit even though the command reports a timeout. Do not infer whether it committed from the command response alone.

Use the operation status and authoritative ledger to reconcile each requested invoice. Reuse the same idempotency key when retrying the same logical operation. Do not create a second payout to compensate for an ambiguous response. Finish only when the durable ledger proves the requested final state.

The API help is available with `python /app/trustval.py --help`. Do not modify the database, environment files, verifier, or task files. Report the final operation IDs and any unresolved item.
