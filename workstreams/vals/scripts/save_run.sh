#!/usr/bin/env bash
# Save a finished Valkyrie run under results/<label>_<run id>/ and re-grade it locally.
# Usage: bash scripts/save_run.sh RUN_ID LABEL
set -euo pipefail
R="$1"; L="$2"; ROOT="$(cd "$(dirname "$0")/.." && pwd)"; O="$ROOT/results/${L}_$R"
mkdir -p "$O"; rm -f "$O/results.json"
timeout 120 valkyrie run results "$R" --path "$O/results.json" </dev/null >/dev/null
timeout 300 valkyrie run outputs "$R" --output-dir "$O/outputs" </dev/null >/dev/null
timeout 120 valkyrie run logs "$R" </dev/null > "$O/run_logs.txt"
python3 "$ROOT/scripts/regrade.py" "$O" > "$O/regrade.json"
python3 - "$O" <<'PY'
import json, sys
from pathlib import Path
o = Path(sys.argv[1])
res = json.loads((o / "results.json").read_text())
reg = json.loads((o / "regrade.json").read_text())
props = res["final_evaluation"]["properties"]
vk = {t: 1.0 for t in props["reward_stats"].get("task_success", {}).get("1.0", [])}
print(res["status"], "errors:", props["n_errors"])
for t, r in reg.items():
    cost = None
    m = o / "outputs" / t / "agent_output/logs/metrics_total.json"
    if m.exists(): cost = json.loads(m.read_text()).get("cost")
    print(f"  {t:20s} valkyrie={vk.get(t, 0.0)} regrade={r['task_success'] if isinstance(r, dict) else r} cost={cost}")
PY
