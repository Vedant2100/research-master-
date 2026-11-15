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
def granted():
    _,st=api("status"); return any(g["user"]==req["user"] and g["role"]==req["role"] and g["status"]=="committed" for g in st)
if not granted():
    rc,_=api("grant",req["user"],req["role"],"--ref",req["reference"])
    if rc!=0 and not wait_for(granted):
        api("grant",req["user"],req["role"],"--ref",req["reference"])
PY
