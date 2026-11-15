import argparse,json,sys
from urllib.error import HTTPError,URLError
from urllib.request import Request,urlopen
BASE="http://trustval-api:8000"
def call(method,path,data=None):
 req=Request(BASE+path,data=None if data is None else json.dumps(data).encode(),method=method,headers={"Content-Type":"application/json"})
 try:
  with urlopen(req,timeout=10) as r: print(r.read().decode())
 except HTTPError as e: print(e.read().decode(),file=sys.stderr); sys.exit(e.code)
 except URLError as e: print(f"API unavailable: {e}",file=sys.stderr); sys.exit(1)
def main():
 p=argparse.ArgumentParser(description="TrustVal inventory API client"); s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("help"); s.add_parser("stock"); s.add_parser("reservations")
 b=s.add_parser("reserve-batch"); b.add_argument("--request",default="/app/request.json")
 a=p.parse_args()
 if a.cmd=="help": p.print_help(); print("\nRequest: /app/request.json"); return
 if a.cmd=="stock": call("GET","/stock")
 elif a.cmd=="reservations": call("GET","/reservations")
 elif a.cmd=="reserve-batch":
  with open(a.request) as f: call("POST","/reserve_batch",json.load(f))
if __name__=="__main__": main()
