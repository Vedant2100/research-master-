import json,sqlite3,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
DB=Path("/state/trustval.db")
def rows(c,sql,args=()): return [dict(x) for x in c.execute(sql,args).fetchall()]
def new_id(prefix): return prefix+uuid.uuid4().hex[:10]
def fault_once(c,name):
 if c.execute("SELECT 1 FROM faults WHERE name=?",(name,)).fetchone(): return False
 c.execute("INSERT INTO faults VALUES(?)",(name,)); return True
class Base(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def send(self,code,obj):
  b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
 def body(self):
  try: return json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
  except Exception: return None
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("CREATE TABLE IF NOT EXISTS invoices(id TEXT PRIMARY KEY,amount INTEGER NOT NULL,status TEXT NOT NULL); CREATE TABLE IF NOT EXISTS payouts(op_id TEXT PRIMARY KEY,reference TEXT NOT NULL,invoice_id TEXT NOT NULL,amount INTEGER NOT NULL,status TEXT NOT NULL); CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,op_id TEXT NOT NULL,event TEXT NOT NULL); CREATE TABLE IF NOT EXISTS faults(name TEXT PRIMARY KEY);")
 return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for x in cfg["invoices"]: c.execute("INSERT OR IGNORE INTO invoices VALUES(?,?,?)",(x["id"],x["amount"],x["status"]))
class H(Base):
 def do_GET(self):
  u=urlparse(self.path); qs=parse_qs(u.query)
  with connect() as c:
   if u.path=="/health": return self.send(200,{"ok":True})
   if u.path=="/invoices": return self.send(200,rows(c,"SELECT * FROM invoices ORDER BY id"))
   if u.path=="/ledger": return self.send(200,rows(c,"SELECT * FROM payouts ORDER BY rowid"))
   if u.path=="/status":
    if qs.get("reference"): return self.send(200,rows(c,"SELECT * FROM payouts WHERE reference=? ORDER BY rowid",(qs["reference"][0],)))
    return self.send(200,rows(c,"SELECT * FROM payouts ORDER BY rowid"))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  d=self.body()
  if d is None: return self.send(400,{"error":"invalid JSON"})
  if self.path!="/pay": return self.send(404,{"error":"unknown endpoint"})
  invoice,amount,ref=d.get("invoice"),d.get("amount"),d.get("reference")
  if not all([invoice,ref]) or not isinstance(amount,int) or amount<=0: return self.send(400,{"error":"invoice, positive amount and reference required"})
  with connect() as c:
   inv=c.execute("SELECT * FROM invoices WHERE id=?",(invoice,)).fetchone()
   if not inv or inv["amount"]!=amount: return self.send(409,{"error":"unknown invoice or amount mismatch"})
   op=new_id("op_")
   c.execute("INSERT INTO payouts VALUES(?,?,?,?,?)",(op,ref,invoice,amount,"committed"))
   c.execute("UPDATE invoices SET status='paid' WHERE id=?",(invoice,))
   c.execute("INSERT INTO events(op_id,event) VALUES(?,?)",(op,"payout_sent"))
   timeout=invoice=="INV-104" and fault_once(c,"pay-timeout")
  if timeout: return self.send(504,{"error":"gateway timeout"})
  self.send(200,{"op_id":op,"status":"committed"})

if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); DB.chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
