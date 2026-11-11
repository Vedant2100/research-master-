#!/usr/bin/env python3
"""Validate file structure only; runs no model or GPU experiments."""
import json
import tomllib
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "portfolio.json").read_text())
projects = data["projects"]
assert len(projects) == 9
assert len({p["id"] for p in projects}) == 9
assert data["track_counts"] == {"memory": 3, "safety": 2, "post-training": 2, "autonomous": 2}
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
print("PASS: 9 thread agents; Copilot + Codex profiles; exact track counts")
