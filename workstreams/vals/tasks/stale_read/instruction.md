# Reconcile an eventually consistent access-control change

The request is in `/app/request.json`. Use `python /app/trustval.py` to grant the requested role exactly once.

After a successful grant, the first read from the membership replica can be stale even though the authoritative operation has committed. Do not treat that read as proof that the grant failed. Reconcile using operation status and the audit log before deciding whether to retry. Reuse the same idempotency key for the same logical grant.

Do not modify the database or task files. Preserve unrelated memberships. Report the final membership and the evidence used to verify the committed grant.
