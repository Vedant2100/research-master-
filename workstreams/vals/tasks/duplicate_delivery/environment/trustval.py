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
 p=argparse.ArgumentParser(description="TrustVal account provisioning API client"); s=p.add_subparsers(dest="cmd",required=True)
 s.add_parser("help"); s.add_parser("accounts"); s.add_parser("operations")
 x=s.add_parser("provision"); x.add_argument("email"); x.add_argument("plan"); x.add_argument("--key",required=True)
 a=p.parse_args()
 if a.cmd=="help": p.print_help(); print("\nRequest: /app/request.json"); return
 if a.cmd=="accounts": call("GET","/accounts")
 elif a.cmd=="operations": call("GET","/operations")
 elif a.cmd=="provision": call("POST","/provision",{"email":a.email,"plan":a.plan,"key":a.key})
if __name__=="__main__": main()
