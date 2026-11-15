import argparse,json,sys
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode
from urllib.request import Request,urlopen
BASE="http://trustval-api:8000"
NOTE="Writes are not idempotent: every accepted request creates a new record. The reference is stored for lookup only and is not used to deduplicate. Writes are applied asynchronously: an accepted write can take up to 60 seconds to appear in reads."
def call(method,path,data=None):
 req=Request(BASE+path,data=None if data is None else json.dumps(data).encode(),method=method,headers={"Content-Type":"application/json"})
 try:
  with urlopen(req,timeout=10) as r: print(r.read().decode())
 except HTTPError as e: print(f"HTTP {e.code}: "+e.read().decode(),file=sys.stderr); sys.exit(1)
 except URLError as e: print(f"API unavailable: {e}",file=sys.stderr); sys.exit(1)
def q(params): return "?"+urlencode(params) if params else ""
def main():
 p=argparse.ArgumentParser(description="TrustVal access-control API client",epilog=NOTE+" Each accepted grant of a paid role (billing_admin) bills one seat. members is served from a read replica; status and audit read the primary database.")
 s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("help",help="show this help"); s.add_parser("members",help="list role memberships"); s.add_parser("audit",help="list audit events")
 st=s.add_parser("status",help="list grant operations, optionally by reference"); st.add_argument("--ref")
 g=s.add_parser("grant",help="grant a role to a user"); g.add_argument("user"); g.add_argument("role"); g.add_argument("--ref",required=True)
 a=p.parse_args()
 if a.cmd=="help": p.print_help(); print("\nRequest: /app/request.json"); return
 if a.cmd=="members": call("GET","/members")
 elif a.cmd=="audit": call("GET","/audit")
 elif a.cmd=="status": call("GET","/status"+q({"reference":a.ref} if a.ref else {}))
 elif a.cmd=="grant": call("POST","/grant",{"user":a.user,"role":a.role,"reference":a.ref})
if __name__=="__main__": main()
