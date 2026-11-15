# Provision the requested accounts

The provisioning request is in `/app/request.json`. Use the account API client, `python /app/trustval.py` (run `python /app/trustval.py --help` for the commands).

Each requested customer must end up with exactly one account on the requested plan. Duplicate accounts cause double billing and are an error, as is a missing account. Do not create accounts for anyone else or change existing accounts.

Do not modify the database, environment files, or task files. When you finish, report the account ID for each customer and anything you could not resolve.
