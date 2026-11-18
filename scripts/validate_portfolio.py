#!/usr/bin/env python3
"""Validate file structure only; runs no model or GPU experiments."""
import json
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "portfolio.json").read_text())
projects = data["projects"]
from collections import Counter
assert projects, "portfolio has no projects"
assert len({p["id"] for p in projects}) == len(projects), "duplicate project ids"
assert data["track_counts"] == dict(Counter(p["track"] for p in projects)), "track_counts disagree with projects"
for p in projects:
    slug = p["id"]
    for filename in (
        f"projects/{slug}.md",
        f"workstreams/{slug}/STATUS.md",
        f".github/agents/{slug}.agent.md",
        f".codex/agents/{slug}.toml",
    ):
        assert (root / filename).is_file(), f"Missing {filename}"
    copilot = (root / f".github/agents/{slug}.agent.md").read_text()
    assert copilot.startswith("---") and "description:" in copilot.split("---", 2)[1]
    codex = tomllib.loads((root / f".codex/agents/{slug}.toml").read_text())
    assert codex["name"] == slug and codex["description"] and codex["developer_instructions"]
print(f"PASS: {len(projects)} thread agents; Copilot + Codex profiles; track counts match projects")
