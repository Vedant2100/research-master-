"""Docker-free check: run each task's sidecar as a local process, apply the naive policy (scripts/naive_cases.inc, must score 0) and solution/solve.sh (must score 1), and grade with the task verifier.

Usage: python scripts/local_policy_test.py [tasks_dir]
"""
import json, re, socket, subprocess, sys, tempfile, time
from pathlib import Path

TASKS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "tasks"
NAIVE = {}
for block in re.findall(r"    (\w+)\)\n(.*?)      ;;", (TASKS.parent / "scripts/naive_cases.inc").read_text(), re.S):
    NAIVE[block[0]] = block[1]


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def run(task: Path, mode: str):
    w = Path(tempfile.mkdtemp(prefix="trustval-"))
    (w / "state").mkdir(); (w / "app").mkdir(); (w / "logs").mkdir()
    port = free_port()
    srv = (task / "environment/state_service/server.py").read_text()
    srv = srv.replace('"/state/trustval.db"', repr(str(w / "state/trustval.db"))).replace('Path("/state")', f"Path({str(w / 'state')!r})")
    srv = srv.replace('"/srv/initial.json"', repr(str(task / "environment/state_service/initial.json"))).replace("8000", str(port))
    (w / "server.py").write_text(srv)
    cli = (task / "environment/trustval.py").read_text().replace("http://trustval-api:8000", f"http://127.0.0.1:{port}").replace("/app/request.json", str(w / "app/request.json"))
    (w / "app/trustval.py").write_text(cli)
    (w / "app/request.json").write_text((task / "environment/request.json").read_text())
    proc = subprocess.Popen([sys.executable, str(w / "server.py")])
    try:
        for _ in range(100):
            try:
                socket.create_connection(("127.0.0.1", port), timeout=0.2).close(); break
            except OSError:
                time.sleep(0.05)
        if mode == "solve":
            script = (task / "solution/solve.sh").read_text()
        else:
            script = "run_agent() { python3 /app/trustval.py \"$@\"; }\n" + NAIVE[task.name]
        script = script.replace("/app/trustval.py", str(w / "app/trustval.py")).replace("/app/request.json", str(w / "app/request.json"))
        subprocess.run(["bash", "-c", script], capture_output=True, timeout=60)
    finally:
        proc.terminate(); proc.wait()
    ver = (task / "tests/verify.py").read_text().replace('"/state/trustval.db"', repr(str(w / "state/trustval.db"))).replace('"/logs/verifier', '"' + str(w / "logs/verifier"))
    subprocess.run([sys.executable, "-c", ver], check=True)
    return json.loads((w / "logs/verifier/reward.json").read_text())


ok = True
for task in sorted(p for p in TASKS.iterdir() if p.is_dir()):
    for mode, want in (("naive", 0.0), ("solve", 1.0)):
        r = run(task, mode)
        good = r["task_success"] == want
        ok &= good
        print(f"{'PASS' if good else 'FAIL'} {task.name:20s} {mode:6s} {r}")
sys.exit(0 if ok else 1)
