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
 p=argparse.ArgumentParser(description="TrustVal supplier payout API client",epilog=NOTE+" ledger and status read the primary database.")
 s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("help",help="show this help"); s.add_parser("invoices",help="list invoices"); s.add_parser("ledger",help="list all payouts")
 st=s.add_parser("status",help="list payouts, optionally by reference"); st.add_argument("--ref")
 x=s.add_parser("pay",help="send a payout for an invoice"); x.add_argument("invoice"); x.add_argument("amount",type=int); x.add_argument("--ref",required=True)
 a=p.parse_args()
 if a.cmd=="help": p.print_help(); print("\nRequest: /app/request.json"); return
 if a.cmd=="invoices": call("GET","/invoices")
 elif a.cmd=="ledger": call("GET","/ledger")
 elif a.cmd=="status": call("GET","/status"+q({"reference":a.ref} if a.ref else {}))
 elif a.cmd=="pay": call("POST","/pay",{"invoice":a.invoice,"amount":a.amount,"reference":a.ref})
if __name__=="__main__": main()
