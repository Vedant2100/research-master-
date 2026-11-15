"""Generate a digest-pinned Valkyrie dataset.toml beside the task folders."""
import hashlib
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TASKS = ROOT / "tasks"

def task_digest(folder: Path) -> str:
    pairs = []
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        relative = path.relative_to(folder).as_posix()
        pairs.append((relative, hashlib.sha256(path.read_bytes()).hexdigest()))
    outer = hashlib.sha256()
    for name, digest in sorted(pairs):
        outer.update(f"{name}\0{digest}\n".encode())
    return "sha256:" + outer.hexdigest()

def main():
    folders = sorted(p for p in TASKS.iterdir() if p.is_dir())
    if not folders:
        raise SystemExit("No task folders found")
    lines = [
        "[dataset]",
        'name = "trustval/stateful-tool-recovery"',
        'version = "v1"',
        'description = "State-changing tool reliability under ambiguous outcomes"',
        'authors = [{ name = "TrustVal" }]',
        'keywords = ["agent-reliability", "idempotency", "tool-use", "state-recovery"]',
        "",
    ]
    for folder in folders:
        task_toml = folder / "task.toml"
        if not task_toml.is_file():
            raise SystemExit(f"Missing {task_toml}")
        task = tomllib.loads(task_toml.read_text(encoding="utf-8"))["task"]
        lines += ["[[tasks]]", f'name = "{task["name"]}"', f'digest = "{task_digest(folder)}"', ""]
    output = TASKS / "dataset.toml"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {output} with {len(folders)} tasks")

if __name__ == "__main__":
    main()
