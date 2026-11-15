#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python - "$ROOT" <<'PY'
import ast, json, pathlib, sys, tomllib
root = pathlib.Path(sys.argv[1])
tasks = sorted(p for p in (root / "tasks").iterdir() if p.is_dir())
assert len(tasks) == 4, f"expected 4 tasks, found {len(tasks)}"
for task in tasks:
    cfg = tomllib.loads((task / "task.toml").read_text())
    assert cfg["task"]["name"].startswith("trustval/")
    assert cfg["environment"]["network_mode"] == "public"
    assert cfg["agent"]["user"] == "root"  # Valkyrie claude_code-v1.0.0 harness installs under /root and /bundle
    assert cfg["verifier"]["user"] == "root"
    assert cfg["verifier"]["environment_mode"] == "separate"
    assert cfg["agent"]["network_mode"] == "allowlist"
    assert "api.anthropic.com" in cfg["agent"]["allowed_hosts"]
    assert "trustval-api" in cfg["agent"]["allowed_hosts"]
    artifact = cfg["artifacts"][0]
    assert artifact["source"] == "/state/trustval.db"
    assert artifact["service"] == "trustval-api"
    for rel in ("instruction.md", "environment/Dockerfile", "environment/docker-compose.yaml",
                "environment/trustval.py", "environment/request.json",
                "environment/state_service/Dockerfile", "environment/state_service/server.py",
                "environment/state_service/initial.json", "tests/test.sh", "tests/verify.py",
                "solution/solve.sh"):
        assert (task / rel).is_file(), f"{task.name}: missing {rel}"
    json.loads((task / "environment/request.json").read_text())
    json.loads((task / "environment/state_service/initial.json").read_text())
    for py in task.rglob("*.py"):
        ast.parse(py.read_text(), filename=str(py))
    print(f"STRUCTURE/TOML/JSON/PYTHON OK: {task.name}")
PY
