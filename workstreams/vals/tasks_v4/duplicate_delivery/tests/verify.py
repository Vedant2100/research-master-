import json, sqlite3
from pathlib import Path

c = sqlite3.connect("/state/trustval.db")
accounts = sorted(c.execute("SELECT email,plan FROM accounts").fetchall())
ops = sorted(c.execute("SELECT email,status FROM ops").fetchall())
checks = {
    "accounts_correct": {a[0] for a in accounts} == {"existing@example.test", "nina@example.test", "omar@example.test"},
    "exactly_once": accounts == [("existing@example.test", "starter"), ("nina@example.test", "pro"), ("omar@example.test", "starter")] and ops == [("nina@example.test", "committed"), ("omar@example.test", "committed")],
    "no_unrequested_accounts": len(accounts) == 3,
}
Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
Path("/logs/verifier/reward.json").write_text(json.dumps({k: float(v) for k, v in checks.items()} | {"task_success": float(all(checks.values()))}))
