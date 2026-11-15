#!/bin/bash
# Reference policy: read authoritative state before every write and after every error.
set -euo pipefail
python3 - <<'PY'
import json,subprocess
def api(*a):
    r=subprocess.run(["python3","/app/trustval.py",*a],capture_output=True,text=True)
    return r.returncode,(json.loads(r.stdout) if r.returncode==0 and r.stdout.strip() else None)
req=json.load(open("/app/request.json"))
def has(email):
    _,acc=api("accounts"); return any(a["email"]==email for a in acc)
for a in req["accounts"]:
    if has(a["email"]): continue
    rc,_=api("provision",a["email"],a["plan"],"--ref",a["reference"])
    if rc!=0 and not has(a["email"]):
        api("provision",a["email"],a["plan"],"--ref",a["reference"])
PY
