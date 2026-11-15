#!/usr/bin/env bash
# For each task, in real containers: the naive policy (scripts/naive_cases.inc) must score 0
# and the reference solution (solution/solve.sh) must score 1.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NAIVE_CASES="$(cat "$ROOT/scripts/naive_cases.inc")"
run_case() {
  local task="$1" mode="$2" want="$3"
  local name envdir base project
  name="$(basename "$task")"; envdir="$task/environment"; base="$envdir/.ci-base-compose.yaml"
  cat > "$base" <<'YAML'
services:
  main:
    build:
      context: .
    command: ["sh", "-c", "sleep infinity"]
YAML
  project="trustval-${name//_/-}-$mode"
  compose=(docker compose -p "$project" -f "$base" -f "$envdir/docker-compose.yaml")
  cleanup() { "${compose[@]}" down -v --remove-orphans >/dev/null 2>&1 || true; rm -f "$base"; }
  trap cleanup EXIT
  "${compose[@]}" up -d --build
  if [[ "$mode" == solve ]]; then
    "${compose[@]}" cp "$task/solution/solve.sh" main:/tmp/solve.sh
    "${compose[@]}" exec -T -u root main bash /tmp/solve.sh
  else
    "${compose[@]}" exec -T -u root main bash -c "run_agent() { python /app/trustval.py \"\$@\"; }
case $name in
$NAIVE_CASES
esac" || true
  fi
  "${compose[@]}" exec -T -u root main mkdir -p /state /tests
  tmpdb="$(mktemp -u)"
  "${compose[@]}" cp trustval-api:/state/trustval.db "$tmpdb"
  "${compose[@]}" cp "$tmpdb" main:/state/trustval.db
  rm -f "$tmpdb"
  "${compose[@]}" cp "$task/tests/verify.py" main:/tests/verify.py
  "${compose[@]}" exec -T -u root main python /tests/verify.py
  reward="$("${compose[@]}" exec -T -u root main cat /logs/verifier/reward.json)"
  printf '%s' "$reward" | python -c "import json,sys; r=json.load(sys.stdin); assert r['task_success'] == $want, r"
  echo "OK: $name $mode -> task_success=$want"
  cleanup; trap - EXIT
}
for task in "$ROOT"/tasks/*; do
  [[ -d "$task" ]] || continue
  run_case "$task" naive 0.0
  run_case "$task" solve 1.0
done
