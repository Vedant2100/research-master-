import json, sqlite3
from pathlib import Path

c = sqlite3.connect("/state/trustval.db")
accounts = c.execute("SELECT email,plan FROM accounts ORDER BY email").fetchall()
ops = c.execute("SELECT key,email,status FROM ops ORDER BY key").fetchall()
accounts_correct = accounts == [
    ("existing@example.test", "starter"),
    ("nina@example.test", "pro"),
    ("omar@example.test", "starter"),
]
exactly_once = ops == [
    ("provision-nina", "nina@example.test", "committed"),
    ("provision-omar", "omar@example.test", "committed"),
]
no_unrequested_accounts = len(accounts) == 3
success = all((accounts_correct, exactly_once, no_unrequested_accounts))
Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
Path("/logs/verifier/reward.json").write_text(json.dumps({
    "task_success": float(success),
    "accounts_correct": float(accounts_correct),
    "exactly_once": float(exactly_once),
    "no_unrequested_accounts": float(no_unrequested_accounts),
}))
