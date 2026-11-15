import json,sqlite3,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
DB=Path("/state/trustval.db")
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("""CREATE TABLE IF NOT EXISTS members(user TEXT,role TEXT,PRIMARY KEY(user,role)); CREATE TABLE IF NOT EXISTS replica(user TEXT,role TEXT,PRIMARY KEY(user,role)); CREATE TABLE IF NOT EXISTS ops(key TEXT PRIMARY KEY,user TEXT,role TEXT,status TEXT); CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,key TEXT,event TEXT); CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value TEXT);""")
 return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for user,role in cfg["members"]:
   c.execute("INSERT OR IGNORE INTO members VALUES(?,?)",(user,role))
   c.execute("INSERT OR IGNORE INTO replica VALUES(?,?)",(user,role))
  c.execute("INSERT OR IGNORE INTO meta VALUES('replica_stale','0')")
def rows(c,sql,args=()): return [dict(x) for x in c.execute(sql,args).fetchall()]
class H(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def send(self,code,obj):
  b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  u=urlparse(self.path); q=parse_qs(u.query)
  with connect() as c:
   if u.path=="/health": return self.send(200,{"ok":True})
   if u.path=="/members":
    out=rows(c,"SELECT * FROM replica ORDER BY user,role")
    stale=c.execute("SELECT value FROM meta WHERE key='replica_stale'").fetchone()[0]=="1"
    if stale:
     c.execute("DELETE FROM replica"); c.execute("INSERT INTO replica SELECT * FROM members")
     c.execute("UPDATE meta SET value='0' WHERE key='replica_stale'")
    return self.send(200,out)
   if u.path=="/audit": return self.send(200,rows(c,"SELECT * FROM events ORDER BY seq"))
   if u.path=="/status": return self.send(200,rows(c,"SELECT * FROM ops"+(" WHERE key=?" if q.get("key") else " ORDER BY key"),(q["key"][0],) if q.get("key") else ()))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  try: d=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
  except Exception: return self.send(400,{"error":"invalid JSON"})
  if self.path!="/grant": return self.send(404,{"error":"unknown endpoint"})
  user,role,key=d.get("user"),d.get("role"),d.get("key")
  if not all([user,role,key]): return self.send(400,{"error":"user, role and key required"})
  with connect() as c:
   old=c.execute("SELECT * FROM ops WHERE key=?",(key,)).fetchone()
   if old: return self.send(200,dict(old))
   c.execute("INSERT OR IGNORE INTO members VALUES(?,?)",(user,role))
   c.execute("INSERT INTO ops VALUES(?,?,?,?)",(key,user,role,"committed"))
   c.execute("INSERT INTO events(key,event) VALUES(?,?)",(key,"grant_committed"))
   c.execute("UPDATE meta SET value='1' WHERE key='replica_stale'")
  self.send(200,{"status":"committed","message":"Grant committed; read replica may lag"})
if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); Path("/state/trustval.db").chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
