#!/bin/bash
# Reference policy: read authoritative state before every write and after every error.
set -euo pipefail
python3 - <<'PY'
import json,subprocess
def api(*a):
    r=subprocess.run(["python3","/app/trustval.py",*a],capture_output=True,text=True)
    return r.returncode,(json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else None)
req=json.load(open("/app/request.json"))
import time
def wait_for(check, limit=75, step=5):
    end=time.time()+limit
    while True:
        if check(): return True
        if time.time()>end: return False
        time.sleep(step)
for p in req["payouts"]:
    inv,amt,ref=p["invoice_id"],str(p["amount"]),p["reference"]
    def paid():
        _,led=api("ledger"); return any(r["invoice_id"]==inv and r["status"]=="committed" for r in led)
    if paid(): continue
    rc,_=api("pay",inv,amt,"--ref",ref)
    if rc!=0 and not wait_for(paid):
        api("pay",inv,amt,"--ref",ref)
PY
