import argparse,json,sys
from urllib.error import HTTPError,URLError
from urllib.parse import urlencode
from urllib.request import Request,urlopen
BASE="http://trustval-api:8000"
def call(method,path,data=None):
 body=None if data is None else json.dumps(data).encode()
 req=Request(BASE+path,data=body,method=method,headers={"Content-Type":"application/json"})
 try:
  with urlopen(req,timeout=10) as r: print(r.read().decode())
 except HTTPError as e:
  print(e.read().decode(),file=sys.stderr); sys.exit(e.code)
 except URLError as e:
  print(f"API unavailable: {e}",file=sys.stderr); sys.exit(1)
def main():
 p=argparse.ArgumentParser(description="TrustVal payout API client")
 s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("help"); s.add_parser("invoices"); s.add_parser("ledger")
 q=s.add_parser("status"); q.add_argument("--key")
 x=s.add_parser("pay"); x.add_argument("invoice"); x.add_argument("amount",type=int); x.add_argument("--key",required=True)
 a=p.parse_args()
 if a.cmd=="help": p.print_help(); print("\nRequest: /app/request.json"); return
 if a.cmd=="invoices": call("GET","/invoices")
 elif a.cmd=="ledger": call("GET","/ledger")
 elif a.cmd=="status": call("GET","/status"+("?"+urlencode({"key":a.key}) if a.key else ""))
 elif a.cmd=="pay": call("POST","/pay",{"invoice":a.invoice,"amount":a.amount,"key":a.key})
if __name__=="__main__": main()
