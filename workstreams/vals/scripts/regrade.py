"""Re-run each task's hidden verifier on a run's saved SQLite artifacts (independent of Valkyrie's grader).

Usage: python scripts/regrade.py results/<run_dir>
"""
import json, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
run_dir = Path(sys.argv[1]).resolve()
out = {}
for task_dir in sorted((ROOT / "tasks").iterdir()):
    if not task_dir.is_dir():
        continue
    db = next((run_dir / "outputs" / task_dir.name / "artifacts").rglob("trustval.db/trustval.db"), None)
    if db is None:
        out[task_dir.name] = "missing artifact"; continue
    with tempfile.TemporaryDirectory() as tmp:
        src = (task_dir / "tests" / "verify.py").read_text()
        src = src.replace('"/state/trustval.db"', repr(str(db))).replace('"/logs/verifier', repr(tmp)[:-1].replace("'", '"', 1))
        subprocess.run([sys.executable, "-I", "-c", src], check=True)
        out[task_dir.name] = json.loads((Path(tmp) / "reward.json").read_text())
print(json.dumps(out, indent=1))
