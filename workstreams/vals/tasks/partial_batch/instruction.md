# Complete the batch while reconciling partial application

The batch request is in `/app/request.json`. Use `python /app/trustval.py reserve-batch` to apply the requested inventory reservations.

The batch operation may commit some items and then return a timeout. Treat that response as ambiguous: inspect the reservation ledger before retrying. Reuse each item's idempotency key. You may safely resubmit the original batch with the same keys; already committed items must not be duplicated, and missing items must be completed.

Preserve the stock of unrequested SKUs. Do not edit the database or task files. Report the final reservation IDs and any item that could not safely be completed.
