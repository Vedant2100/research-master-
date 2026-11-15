import json, sqlite3
from pathlib import Path

c = sqlite3.connect("/state/trustval.db")
members = set(c.execute("SELECT user,role FROM members"))
ops = c.execute("SELECT key,user,role,status FROM ops").fetchall()
events = c.execute("SELECT count(*) FROM events").fetchone()[0]
role_granted = ("maya", "billing_admin") in members
existing_state_preserved = {
    ("maya", "viewer"),
    ("maya", "support_agent"),
    ("liam", "billing_admin"),
}.issubset(members)
exactly_once = ops == [("grant-maya-billing", "maya", "billing_admin", "committed")] and events == 1
success = all((role_granted, existing_state_preserved, exactly_once))
Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
Path("/logs/verifier/reward.json").write_text(json.dumps({
    "task_success": float(success),
    "role_granted": float(role_granted),
    "existing_state_preserved": float(existing_state_preserved),
    "exactly_once": float(exactly_once),
}))
