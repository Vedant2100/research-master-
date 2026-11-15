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
 c.executescript("CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY,email TEXT,plan TEXT); CREATE TABLE IF NOT EXISTS ops(id TEXT PRIMARY KEY,reference TEXT,account_id TEXT,email TEXT,status TEXT); CREATE TABLE IF NOT EXISTS faults(name TEXT PRIMARY KEY);")
 return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for aid,email,plan in cfg["accounts"]: c.execute("INSERT OR IGNORE INTO accounts VALUES(?,?,?)",(aid,email,plan))
class H(Base):
 def do_GET(self):
  with connect() as c:
   if self.path=="/health": return self.send(200,{"ok":True})
   if self.path=="/accounts": return self.send(200,rows(c,"SELECT * FROM accounts ORDER BY rowid"))
   if self.path=="/operations": return self.send(200,rows(c,"SELECT * FROM ops ORDER BY rowid"))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  d=self.body()
  if d is None: return self.send(400,{"error":"invalid JSON"})
  if self.path!="/provision": return self.send(404,{"error":"unknown endpoint"})
  email,plan,ref=d.get("email"),d.get("plan"),d.get("reference")
  if not all([email,plan,ref]): return self.send(400,{"error":"email, plan and reference required"})
  with connect() as c:
   aid=new_id("acct_")
   c.execute("INSERT INTO accounts VALUES(?,?,?)",(aid,email,plan)); c.execute("INSERT INTO ops VALUES(?,?,?,?,?)",(new_id("op_"),ref,aid,email,"committed"))
   reset=email=="nina@example.test" and fault_once(c,"provision-reset")
  if reset: return self.send(502,{"error":"connection reset by upstream"})
  self.send(200,{"account_id":aid,"status":"committed"})

if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); DB.chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
