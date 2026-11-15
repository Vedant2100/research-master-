import json,sqlite3,uuid
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from pathlib import Path
DB=Path("/state/trustval.db")
def connect():
 DB.parent.mkdir(parents=True,exist_ok=True); c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript("""CREATE TABLE IF NOT EXISTS stock(sku TEXT PRIMARY KEY,qty INTEGER); CREATE TABLE IF NOT EXISTS reservations(id TEXT PRIMARY KEY,key TEXT UNIQUE,sku TEXT,qty INTEGER,status TEXT); CREATE TABLE IF NOT EXISTS faults(key TEXT PRIMARY KEY);""")
 return c
def seed():
 cfg=json.loads(Path("/srv/initial.json").read_text())
 with connect() as c:
  for sku,qty in cfg["stock"]: c.execute("INSERT OR IGNORE INTO stock VALUES(?,?)",(sku,qty))
def rows(c,sql): return [dict(x) for x in c.execute(sql).fetchall()]
def reserve(c,item):
 key,sku,qty=item["idempotency_key"],item["sku"],item["quantity"]
 old=c.execute("SELECT * FROM reservations WHERE key=?",(key,)).fetchone()
 if old: return dict(old)
 row=c.execute("SELECT qty FROM stock WHERE sku=?",(sku,)).fetchone()
 if not row or not isinstance(qty,int) or qty<=0 or row["qty"]<qty: raise ValueError("insufficient stock for "+str(sku))
 rid="r_"+uuid.uuid4().hex[:10]
 c.execute("UPDATE stock SET qty=qty-? WHERE sku=?",(qty,sku)); c.execute("INSERT INTO reservations VALUES(?,?,?,?,?)",(rid,key,sku,qty,"committed"))
 return {"id":rid,"key":key,"sku":sku,"qty":qty,"status":"committed"}
class H(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def send(self,code,obj):
  b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
 def do_GET(self):
  with connect() as c:
   if self.path=="/health": return self.send(200,{"ok":True})
   if self.path=="/stock": return self.send(200,rows(c,"SELECT * FROM stock ORDER BY sku"))
   if self.path=="/reservations": return self.send(200,rows(c,"SELECT * FROM reservations ORDER BY key"))
  self.send(404,{"error":"unknown endpoint"})
 def do_POST(self):
  try: d=json.loads(self.rfile.read(int(self.headers.get("Content-Length","0"))))
  except Exception: return self.send(400,{"error":"invalid JSON"})
  if self.path!="/reserve_batch": return self.send(404,{"error":"unknown endpoint"})
  items=d.get("reservations")
  if not isinstance(items,list) or not items: return self.send(400,{"error":"reservations list required"})
  completed=[]
  for item in items:
   try:
    with connect() as c: result=reserve(c,item)
   except (ValueError,KeyError,TypeError) as e: return self.send(409,{"error":str(e),"completed":completed})
   completed.append(result)
   if item.get("idempotency_key")=="reserve-B":
    with connect() as c:
     seen=c.execute("SELECT 1 FROM faults WHERE key='batch-interrupted'").fetchone()
     if not seen:
      c.execute("INSERT INTO faults VALUES('batch-interrupted')")
      return self.send(504,{"error":"batch interrupted after durable partial commit","completed":completed})
  self.send(200,{"status":"committed","reservations":completed})
if __name__=="__main__":
 Path("/state").mkdir(exist_ok=True); seed(); Path("/state/trustval.db").chmod(0o600)
 ThreadingHTTPServer(("0.0.0.0",8000),H).serve_forever()
