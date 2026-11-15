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
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("CREATE TABLE IF NOT EXISTS stock(sku TEXT PRIMARY KEY,qty INTEGER); CREATE TABLE IF NOT EXISTS reservations(id TEXT PRIMARY KEY,reference TEXT,sku TEXT,qty INTEGER,status TEXT,visible_at REAL NOT NULL DEFAULT 0); CREATE TABLE IF NOT EXISTS faults(name TEXT PRIMARY KEY);")
 return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for sku,qty in cfg["stock"]: c.execute("INSERT OR IGNORE INTO stock VALUES(?,?)",(sku,qty))
def reserve(c,item):
 ref,sku,qty=item.get("reference"),item.get("sku"),item.get("quantity")
 if not ref or not sku: raise ValueError("sku and reference required")
 row=c.execute("SELECT qty FROM stock WHERE sku=?",(sku,)).fetchone()
 if not row or not isinstance(qty,int) or qty<=0 or row["qty"]<qty: raise ValueError("insufficient stock for "+str(sku))
 rid=new_id("r_")
 c.execute("UPDATE stock SET qty=qty-? WHERE sku=?",(qty,sku)); c.execute("INSERT INTO reservations VALUES(?,?,?,?,?,0)",(rid,ref,sku,qty,"committed"))
 return {"id":rid,"reference":ref,"sku":sku,"qty":qty,"status":"committed"}
class H(Base):
 def do_GET(self):
  with connect() as c:
   if self.path=="/health": return self.send(200,{"ok":True})
   if self.path=="/stock": return self.send(200,rows(c,"SELECT s.sku,s.qty+COALESCE((SELECT SUM(r.qty) FROM reservations r WHERE r.sku=s.sku AND r.visible_at>?),0) AS qty FROM stock s ORDER BY s.sku",(now(),)))
   if self.path=="/reservations": return self.send(200,rows(c,"SELECT id,reference,sku,qty,status FROM reservations WHERE visible_at<=? ORDER BY rowid",(now(),)))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  d=self.body()
  if d is None: return self.send(400,{"error":"invalid JSON"})
  if self.path=="/reserve":
   try:
    with connect() as c: return self.send(200,reserve(c,d))
   except ValueError as e: return self.send(409,{"error":str(e)})
  if self.path!="/reserve_batch": return self.send(404,{"error":"unknown endpoint"})
  items=d.get("reservations")
  if not isinstance(items,list) or not items: return self.send(400,{"error":"reservations list required"})
  done=[]
  for item in items:
   try:
    with connect() as c: done.append(reserve(c,item))
   except (ValueError,TypeError,AttributeError) as e: return self.send(409,{"error":str(e)})
   if item.get("reference")=="reserve-B":
    with connect() as c:
     timeout=fault_once(c,"batch-timeout")
     if timeout:
      for d0 in done: c.execute("UPDATE reservations SET visible_at=? WHERE id=?",(now()+DELAY,d0["id"]))
    if timeout: return self.send(504,{"error":"gateway timeout"})
  self.send(200,{"status":"committed","reservations":done})

if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); DB.chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
