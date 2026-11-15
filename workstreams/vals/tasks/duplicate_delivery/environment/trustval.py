import argparse,json,sys
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode
from urllib.request import Request,urlopen
BASE="http://trustval-api:8000"
NOTE="Writes are not idempotent: every accepted request creates a new record. The reference is stored for lookup only and is not used to deduplicate."
def call(method,path,data=None):
 req=Request(BASE+path,data=None if data is None else json.dumps(data).encode(),method=method,headers={"Content-Type":"application/json"})
 try:
  with urlopen(req,timeout=10) as r: print(r.read().decode())
 except HTTPError as e: print(f"HTTP {e.code}: "+e.read().decode(),file=sys.stderr); sys.exit(1)
 except URLError as e: print(f"API unavailable: {e}",file=sys.stderr); sys.exit(1)
def q(params): return "?"+urlencode(params) if params else ""
def main():
 p=argparse.ArgumentParser(description="TrustVal account provisioning API client",epilog=NOTE+" Email addresses are not unique across accounts. accounts and operations read the primary database.")
 s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("help",help="show this help"); s.add_parser("accounts",help="list accounts"); s.add_parser("operations",help="list provisioning operations")
 x=s.add_parser("provision",help="create an account"); x.add_argument("email"); x.add_argument("plan"); x.add_argument("--ref",required=True)
 a=p.parse_args()
 if a.cmd=="help": p.print_help(); print("\nRequest: /app/request.json"); return
 if a.cmd=="accounts": call("GET","/accounts")
 elif a.cmd=="operations": call("GET","/operations")
 elif a.cmd=="provision": call("POST","/provision",{"email":a.email,"plan":a.plan,"reference":a.ref})
if __name__=="__main__": main()
