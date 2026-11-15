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
 p=argparse.ArgumentParser(description="TrustVal inventory API client",epilog=NOTE+" Items in a batch are applied one at a time, in order. stock and reservations read the primary database.")
 s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("help",help="show this help"); s.add_parser("stock",help="list stock levels"); s.add_parser("reservations",help="list all reservations")
 b=s.add_parser("reserve-batch",help="reserve every item in a request file"); b.add_argument("--request",default="/app/request.json")
 r=s.add_parser("reserve",help="reserve one item"); r.add_argument("sku"); r.add_argument("quantity",type=int); r.add_argument("--ref",required=True)
 a=p.parse_args()
 if a.cmd=="help": p.print_help(); print("\nRequest: /app/request.json"); return
 if a.cmd=="stock": call("GET","/stock")
 elif a.cmd=="reservations": call("GET","/reservations")
 elif a.cmd=="reserve-batch":
  with open(a.request) as f: call("POST","/reserve_batch",json.load(f))
 elif a.cmd=="reserve": call("POST","/reserve",{"sku":a.sku,"quantity":a.quantity,"reference":a.ref})
if __name__=="__main__": main()
