import json,sqlite3,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
DB=Path("/state/trustval.db")
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("CREATE TABLE IF NOT EXISTS accounts(id TEXT PRIMARY KEY,email TEXT UNIQUE,plan TEXT); CREATE TABLE IF NOT EXISTS ops(key TEXT PRIMARY KEY,account_id TEXT,email TEXT,status TEXT);"); return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for x in cfg["accounts"]: c.execute("INSERT OR IGNORE INTO accounts VALUES(?,?,?)",tuple(x))
def rows(c,sql): return [dict(x) for x in c.execute(sql).fetchall()]
class H(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def send(self,code,obj):
  b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  with connect() as c:
   if self.path=="/health": return self.send(200,{"ok":True})
   if self.path=="/accounts": return self.send(200,rows(c,"SELECT * FROM accounts ORDER BY email"))
   if self.path=="/operations": return self.send(200,rows(c,"SELECT * FROM ops ORDER BY key"))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  try: d=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
  except Exception: return self.send(400,{"error":"invalid JSON"})
  if self.path!="/provision": return self.send(404,{"error":"unknown endpoint"})
  email,plan,key=d.get("email"),d.get("plan"),d.get("key")
  if not all([email,plan,key]): return self.send(400,{"error":"email, plan and key required"})
  with connect() as c:
   old=c.execute("SELECT * FROM ops WHERE key=?",(key,)).fetchone()
   if old: return self.send(200,dict(old))
   if c.execute("SELECT 1 FROM accounts WHERE email=?",(email,)).fetchone(): return self.send(409,{"error":"account exists under a different operation key"})
   aid="acct_"+uuid.uuid4().hex[:10]
   c.execute("INSERT INTO accounts VALUES(?,?,?)",(aid,email,plan)); c.execute("INSERT INTO ops VALUES(?,?,?,?)",(key,aid,email,"committed"))
  if email=="nina@example.test": return self.send(504,{"error":"connection lost after durable commit","key":key})
  self.send(200,{"account_id":aid,"status":"committed"})
if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); Path("/state/trustval.db").chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
