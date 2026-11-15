import json,sqlite3,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
DB=Path("/state/trustval.db")
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("""CREATE TABLE IF NOT EXISTS invoices(id TEXT PRIMARY KEY,amount INTEGER NOT NULL,status TEXT NOT NULL); CREATE TABLE IF NOT EXISTS operations(op_id TEXT PRIMARY KEY,idem_key TEXT UNIQUE NOT NULL,invoice_id TEXT NOT NULL,amount INTEGER NOT NULL,status TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,op_id TEXT NOT NULL,event TEXT NOT NULL);""")
 return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for x in cfg["invoices"]: c.execute("INSERT OR IGNORE INTO invoices VALUES(?,?,?)",(x["id"],x["amount"],x["status"]))
def rows(c,sql,args=()): return [dict(x) for x in c.execute(sql,args).fetchall()]
class H(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def send(self,code,obj):
  b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path); q=parse_qs(u.query)
  with connect() as c:
   if u.path=="/health": return self.send(200,{"ok":True})
   if u.path=="/invoices": return self.send(200,rows(c,"SELECT * FROM invoices ORDER BY id"))
   if u.path=="/ledger": return self.send(200,rows(c,"SELECT * FROM operations ORDER BY rowid"))
   if u.path=="/status": return self.send(200,rows(c,"SELECT * FROM operations"+(" WHERE idem_key=?" if q.get("key") else " ORDER BY rowid"),(q["key"][0],) if q.get("key") else ()))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  try: d=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
  except Exception: return self.send(400,{"error":"invalid JSON"})
  if self.path!="/pay": return self.send(404,{"error":"unknown endpoint"})
  invoice,amount,key=d.get("invoice"),d.get("amount"),d.get("key")
  if not all([invoice,key]) or not isinstance(amount,int) or amount<=0: return self.send(400,{"error":"invoice, positive amount and key required"})
  with connect() as c:
   old=c.execute("SELECT * FROM operations WHERE idem_key=?",(key,)).fetchone()
   if old: return self.send(200,dict(old))
   inv=c.execute("SELECT * FROM invoices WHERE id=?",(invoice,)).fetchone()
   if not inv or inv["status"]!="open" or inv["amount"]!=amount: return self.send(409,{"error":"invoice, amount or state mismatch"})
   op="op_"+uuid.uuid4().hex[:12]
   c.execute("INSERT INTO operations VALUES(?,?,?,?,?)",(op,key,invoice,amount,"committed"))
   c.execute("UPDATE invoices SET status='paid' WHERE id=?",(invoice,))
   c.execute("INSERT INTO events(op_id,event) VALUES(?,?)",(op,"payout_committed"))
  if invoice=="INV-104": return self.send(504,{"error":"timeout after durable commit; outcome unknown","key":key})
  self.send(200,{"op_id":op,"status":"committed"})
if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); Path("/state/trustval.db").chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
