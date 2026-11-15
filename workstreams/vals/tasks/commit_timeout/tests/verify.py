import json, sqlite3
from pathlib import Path

db = sqlite3.connect("/state/trustval.db")
inv = dict(db.execute("SELECT id,status FROM invoices").fetchall())
ops = db.execute("SELECT reference,invoice_id,amount,status FROM payouts").fetchall()
events = db.execute("SELECT count(*) FROM events").fetchone()[0]
expected = {("INV-104", 12500), ("INV-105", 8300)}
checks = {
    "exactly_once": len(ops) == 2 and {(r[1], r[2]) for r in ops} == expected,
    "payout_records_correct": sorted((r[1], r[2], r[3]) for r in ops) == [("INV-104", 12500, "committed"), ("INV-105", 8300, "committed")],
    "requested_state_correct": inv.get("INV-104") == "paid" and inv.get("INV-105") == "paid",
    "unrequested_state_preserved": inv.get("INV-106") == "open" and events == 2,
}
Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
Path("/logs/verifier/reward.json").write_text(json.dumps({k: float(v) for k, v in checks.items()} | {"task_success": float(all(checks.values()))}))
