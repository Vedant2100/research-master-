import json,sqlite3,uuid,time
DELAY=30  # seconds before a write that hit a fault becomes visible to reads
def now(): return time.time()
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
PAID_SEATS={"billing_admin":40}
STALE_READS=3
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("CREATE TABLE IF NOT EXISTS members(user TEXT,role TEXT,PRIMARY KEY(user,role)); CREATE TABLE IF NOT EXISTS replica(user TEXT,role TEXT,PRIMARY KEY(user,role)); CREATE TABLE IF NOT EXISTS grants(id TEXT PRIMARY KEY,reference TEXT,user TEXT,role TEXT,status TEXT,visible_at REAL NOT NULL DEFAULT 0); CREATE TABLE IF NOT EXISTS seat_charges(id TEXT PRIMARY KEY,grant_id TEXT,role TEXT,amount INTEGER); CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY AUTOINCREMENT,grant_id TEXT,event TEXT,visible_at REAL NOT NULL DEFAULT 0); CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY,value REAL); CREATE TABLE IF NOT EXISTS faults(name TEXT PRIMARY KEY);")
 return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for user,role in cfg["members"]:
   c.execute("INSERT OR IGNORE INTO members VALUES(?,?)",(user,role)); c.execute("INSERT OR IGNORE INTO replica VALUES(?,?)",(user,role))
  c.execute("INSERT OR IGNORE INTO meta VALUES('members_visible_at',0)")
def sync(c):
 c.execute("DELETE FROM replica"); c.execute("INSERT INTO replica SELECT * FROM members")
class H(Base):
 def do_GET(self):
  u=urlparse(self.path); qs=parse_qs(u.query)
  with connect() as c:
   if u.path=="/health": return self.send(200,{"ok":True})
   if u.path=="/members":
    if c.execute("SELECT value FROM meta WHERE key='members_visible_at'").fetchone()[0]<=now(): sync(c)
    return self.send(200,rows(c,"SELECT * FROM replica ORDER BY user,role"))
   if u.path=="/audit": return self.send(200,rows(c,"SELECT seq,grant_id,event FROM events WHERE visible_at<=? ORDER BY seq",(now(),)))
   if u.path=="/status":
    G="SELECT id,reference,user,role,status FROM grants WHERE visible_at<=?"
    if qs.get("reference"): return self.send(200,rows(c,G+" AND reference=? ORDER BY rowid",(now(),qs["reference"][0])))
    return self.send(200,rows(c,G+" ORDER BY rowid",(now(),)))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  d=self.body()
  if d is None: return self.send(400,{"error":"invalid JSON"})
  if self.path!="/grant": return self.send(404,{"error":"unknown endpoint"})
  user,role,ref=d.get("user"),d.get("role"),d.get("reference")
  if not all([user,role,ref]): return self.send(400,{"error":"user, role and reference required"})
  with connect() as c:
   gid=new_id("g_")
   timeout=fault_once(c,"grant-timeout"); vis=now()+DELAY if timeout else 0
   if not timeout: sync(c)
   c.execute("INSERT OR IGNORE INTO members VALUES(?,?)",(user,role))
   c.execute("INSERT INTO grants VALUES(?,?,?,?,?,?)",(gid,ref,user,role,"committed",vis))
   c.execute("INSERT INTO events(grant_id,event,visible_at) VALUES(?,?,?)",(gid,"role_granted",vis))
   if role in PAID_SEATS:
    c.execute("INSERT INTO seat_charges VALUES(?,?,?,?)",(new_id("ch_"),gid,role,PAID_SEATS[role])); c.execute("INSERT INTO events(grant_id,event,visible_at) VALUES(?,?,?)",(gid,"seat_charged",vis))
   if timeout: c.execute("UPDATE meta SET value=? WHERE key='members_visible_at'",(vis,))
  if timeout: return self.send(504,{"error":"gateway timeout"})
  self.send(200,{"status":"accepted"})

if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); DB.chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
