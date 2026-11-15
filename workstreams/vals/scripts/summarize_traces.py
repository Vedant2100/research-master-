"""Print each task's tool calls and results from a saved run, for trace analysis.

Usage: python scripts/summarize_traces.py results/<run_dir> [max_chars]
"""
import json
import sys
from pathlib import Path

run_dir = Path(sys.argv[1])
width = int(sys.argv[2]) if len(sys.argv) > 2 else 200

for traj in sorted(run_dir.glob("outputs/*/agent_output/logs/trajectory.jsonl")):
    task = traj.parts[-4]
    print(f"===== {task}")
    for line in traj.read_text().splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = event.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for c in content:
            kind = c.get("type")
            if kind == "tool_use":
                inp = c.get("input") or {}
                print(">>", str(inp.get("command") or json.dumps(inp))[:width])
            elif kind == "tool_result":
                out = c.get("content")
                out = out if isinstance(out, str) else json.dumps(out)
                print("   <<", out.replace("\n", " | ")[:width])
            elif kind == "text" and msg.get("role") == "assistant":
                print("AI:", c["text"].replace("\n", " ")[:width])
