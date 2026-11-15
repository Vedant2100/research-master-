"""Aggregate saved runs for one dataset version into a table (JSON + Markdown) and a chart.

Uses the locally re-graded rewards (regrade.json) and checks they agree with Valkyrie's.
Usage: python scripts/aggregate.py v3
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
VERSION = sys.argv[1] if len(sys.argv) > 1 else "v3"
TASKS = ["commit_timeout", "stale_read", "partial_batch", "duplicate_delivery"]
MODELS = {"haiku45": "Claude Haiku 4.5", "sonnet46": "Claude Sonnet 4.6"}
COLORS = {"haiku45": "#2a78d6", "sonnet46": "#eb6834"}  # categorical slots 1-2 (validated)
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e1e0d9", "#fcfcfb"

runs = defaultdict(list)
for d in sorted((ROOT / "results").glob(f"*-{VERSION}-t*_*")):
    label, run_id = d.name.split("_", 1)
    model = label.split("-")[0]
    reg = json.loads((d / "regrade.json").read_text())
    res = json.loads((d / "results.json").read_text())
    vk = set(res["final_evaluation"]["properties"]["reward_stats"].get("task_success", {}).get("1.0", []))
    cost = 0.0
    for t in TASKS:
        m = d / "outputs" / t / "agent_output/logs/metrics_total.json"
        if m.exists():
            cost += json.loads(m.read_text()).get("cost") or 0.0
        assert (reg[t]["task_success"] == 1.0) == (t in vk), f"regrade disagrees with Valkyrie: {d.name} {t}"
    runs[model].append({"label": label, "run_id": run_id, "success": {t: reg[t]["task_success"] for t in TASKS}, "cost_usd": round(cost, 4)})

summary = {"dataset_version": VERSION, "models": {}}
for model, rs in runs.items():
    n = len(rs)
    per_task = {t: sum(r["success"][t] for r in rs) for t in TASKS}
    summary["models"][model] = {
        "name": MODELS.get(model, model), "trials": n, "runs": rs,
        "passes_per_task": per_task, "mean_task_success": round(sum(per_task.values()) / (n * len(TASKS)), 3),
        "total_cost_usd": round(sum(r["cost_usd"] for r in rs), 3),
    }
out = ROOT / "results" / f"summary_{VERSION}.json"
out.write_text(json.dumps(summary, indent=1))

lines = ["| Model | Trials | " + " | ".join(TASKS) + " | Mean task_success | Agent cost (USD) |",
         "|---|---:|" + "---:|" * len(TASKS) + "---:|---:|"]
for model, s in summary["models"].items():
    cells = " | ".join(f"{int(s['passes_per_task'][t])}/{s['trials']}" for t in TASKS)
    lines.append(f"| {s['name']} | {s['trials']} | {cells} | {s['mean_task_success']:.2f} | {s['total_cost_usd']:.2f} |")
(ROOT / "results" / f"summary_{VERSION}.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))

# Chart: grouped bars, passes out of n per task, one hue per model, direct labels.
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=160)
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
models = [m for m in MODELS if m in summary["models"]]
width, gap = 0.36, 0.02
for i, model in enumerate(models):
    s = summary["models"][model]
    xs = [k + (i - (len(models) - 1) / 2) * (width + gap) for k in range(len(TASKS))]
    vals = [s["passes_per_task"][t] for t in TASKS]
    ax.bar(xs, vals, width=width, color=COLORS[model], label=f"{s['name']} (n={s['trials']})", zorder=2)
    for x, v in zip(xs, vals):
        ax.text(x, v + 0.06, f"{int(v)}/{s['trials']}", ha="center", va="bottom", fontsize=9, color=INK2)
n_max = max(summary["models"][m]["trials"] for m in models)
ax.set_xticks(range(len(TASKS)), [t.replace("_", " ") for t in TASKS], color=INK, fontsize=10)
ax.set_ylim(0, n_max + 0.6); ax.set_yticks(range(n_max + 1))
ax.set_ylabel("Trials passed", color=INK2, fontsize=10)
ax.tick_params(colors=INK2, length=0)
ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
for side in ("top", "right", "left"): ax.spines[side].set_visible(False)
ax.spines["bottom"].set_color(GRID)
ax.set_title(f"TrustVal {VERSION}: tasks passed per model (Claude Code harness, Valkyrie)", color=INK, fontsize=11, loc="left")
ax.legend(frameon=False, fontsize=9, labelcolor=INK, loc="upper right")
fig.tight_layout()
fig.savefig(ROOT / "results" / f"results_{VERSION}.png", facecolor=SURFACE)
print("wrote", out.name, f"summary_{VERSION}.md", f"results_{VERSION}.png")
