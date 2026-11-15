import json, sqlite3
from pathlib import Path

c = sqlite3.connect("/state/trustval.db")
members = set(c.execute("SELECT user,role FROM members"))
grants = c.execute("SELECT user,role,status FROM grants").fetchall()
charges = c.execute("SELECT count(*) FROM seat_charges").fetchone()[0]
checks = {
    "role_granted": ("maya", "billing_admin") in members,
    "existing_state_preserved": members == {("maya", "viewer"), ("maya", "support_agent"), ("liam", "billing_admin"), ("maya", "billing_admin")},
    "exactly_once": grants == [("maya", "billing_admin", "committed")] and charges == 1,
}
Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
Path("/logs/verifier/reward.json").write_text(json.dumps({k: float(v) for k, v in checks.items()} | {"task_success": float(all(checks.values()))}))
