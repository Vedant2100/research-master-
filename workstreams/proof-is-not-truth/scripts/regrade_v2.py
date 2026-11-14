"""Offline regrading script for Proof Is Not Truth evaluation traces.

Performs offline regrading directly from the immutable evaluation_traces.json.
Fixes action-ordering:
- Flags unsafe action attempts even if later actions attempt to undo them.
- Disallows safe_abstention / valid_abstention if an unsafe write occurred prior to abstention.
- Distinguishes attempted mutations from final-state safety.
"""
from __future__ import annotations
import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure src is in python path
src_dir = Path(__file__).resolve().parent.parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from cases import get_all_cases
from sandbox import grade_trace, EpistemicCase
from agent_eval import aggregate_metrics


def regrade_traces(traces_path: Path, output_dir: Path) -> Dict[str, Any]:
    with traces_path.open("r", encoding="utf-8") as f:
        traces = json.load(f)

    cases_map = {c.case_id: c for c in get_all_cases()}
    regraded_results = []
    regraded_traces = []

    for item in traces:
        case_id = item["case_id"]
        condition = item["condition"]
        seed = item.get("seed", 42)
        trace = item["trace"]
        case = cases_map[case_id]

        regraded = grade_trace(trace, case)
        regraded.update({
            "condition": condition,
            "mode": item.get("grade", {}).get("mode", "llm"),
            "model": item.get("grade", {}).get("model", "qwen2.5:7b"),
            "seed": seed,
            "case_id": case_id,
            "split": case.split
        })
        regraded_results.append(regraded)
        regraded_traces.append({
            "case_id": case_id,
            "condition": condition,
            "seed": seed,
            "split": case.split,
            "grade": regraded,
            "trace": trace
        })

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Write regraded CSV
    csv_path = output_dir / "evaluation_results_regraded_v2.csv"
    if regraded_results:
        with csv_path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(regraded_results[0].keys()))
            writer.writeheader()
            writer.writerows(regraded_results)

    # 2. Write regraded traces
    traces_v2_path = output_dir / "evaluation_traces_regraded_v2.json"
    traces_v2_path.write_text(json.dumps(regraded_traces, indent=2), encoding="utf-8")

    # 3. Write regraded metrics summary
    summary = aggregate_metrics(regraded_results)
    summary_path = output_dir / "metrics_summary_regraded_v2.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    return summary


def main():
    repo_root = Path(__file__).resolve().parent.parent
    runs_dir = repo_root / "runs" / "qwen25_7b_full"
    traces_path = runs_dir / "evaluation_traces.json"

    if not traces_path.exists():
        print(f"Error: {traces_path} not found.")
        sys.exit(1)

    print(f"Executing offline regrade v2 from {traces_path}...")
    summary = regrade_traces(traces_path, runs_dir)
    print("=== Regraded Metrics Summary v2 ===")
    print(json.dumps(summary, indent=2))
    print(f"\nRegraded artifacts saved to: {runs_dir}")


if __name__ == "__main__":
    main()
