import json, sqlite3
from pathlib import Path

db = sqlite3.connect("/state/trustval.db")
inv = dict(db.execute("SELECT id,status FROM invoices").fetchall())
ops = db.execute("SELECT idem_key,invoice_id,amount,status FROM operations").fetchall()
events = db.execute("SELECT count(*) FROM events").fetchone()[0]
expected = {
    "payout-INV-104": ("INV-104", 12500),
    "payout-INV-105": ("INV-105", 8300),
}
exactly_once = len(ops) == 2 and len({r[0] for r in ops}) == 2
payout_records_correct = {r[0]: (r[1], r[2]) for r in ops} == expected and all(r[3] == "committed" for r in ops)
requested_state_correct = inv.get("INV-104") == "paid" and inv.get("INV-105") == "paid"
unrequested_state_preserved = inv.get("INV-106") == "open" and events == 2
success = all((exactly_once, payout_records_correct, requested_state_correct, unrequested_state_preserved))
Path("/logs/verifier").mkdir(parents=True, exist_ok=True)
Path("/logs/verifier/reward.json").write_text(json.dumps({
    "task_success": float(success),
    "exactly_once": float(exactly_once),
    "payout_records_correct": float(payout_records_correct),
    "requested_state_correct": float(requested_state_correct),
    "unrequested_state_preserved": float(unrequested_state_preserved),
}))
