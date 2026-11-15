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
def have(sku):
    _,rs=api("reservations"); return any(r["sku"]==sku and r["status"]=="committed" for r in rs)
for it in req["reservations"]:
    if have(it["sku"]): continue
    rc,_=api("reserve",it["sku"],str(it["quantity"]),"--ref",it["reference"])
    if rc!=0 and not wait_for(lambda: have(it["sku"])):
        api("reserve",it["sku"],str(it["quantity"]),"--ref",it["reference"])
PY
