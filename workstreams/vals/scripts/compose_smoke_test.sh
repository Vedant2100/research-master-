#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
for task in "$ROOT"/tasks/*; do
  [[ -d "$task" ]] || continue
  name="$(basename "$task")"
  envdir="$task/environment"
  base="$envdir/.ci-base-compose.yaml"
  cat > "$base" <<'YAML'
services:
  main:
    build:
      context: .
    command: ["sh", "-c", "sleep infinity"]
YAML
  project="trustval-${name//_/-}"
  compose=(docker compose -p "$project" -f "$base" -f "$envdir/docker-compose.yaml")
  cleanup() { "${compose[@]}" down -v --remove-orphans >/dev/null 2>&1 || true; rm -f "$base"; }
  trap cleanup EXIT
  "${compose[@]}" up -d --build
  run_agent() { "${compose[@]}" exec -T -u agent main python /app/trustval.py "$@"; }
  case "$name" in
    commit_timeout)
      if run_agent pay INV-104 12500 --key payout-INV-104; then
        echo "Expected commit-timeout fault did not occur" >&2; exit 1
      fi
      run_agent status --key payout-INV-104
      run_agent pay INV-104 12500 --key payout-INV-104
      run_agent pay INV-105 8300 --key payout-INV-105
      ;;
    stale_read)
      run_agent grant maya billing_admin --key grant-maya-billing
      first="$(run_agent members)"
      second="$(run_agent members)"
      printf '%s' "$first" | python -c 'import json,sys; x=json.load(sys.stdin); assert ["maya","billing_admin"] not in [[r["user"],r["role"]] for r in x]'
      printf '%s' "$second" | python -c 'import json,sys; x=json.load(sys.stdin); assert ["maya","billing_admin"] in [[r["user"],r["role"]] for r in x]'
      run_agent status --key grant-maya-billing
      run_agent audit
      ;;
    partial_batch)
      if run_agent reserve-batch; then
        echo "Expected partial-batch fault did not occur" >&2; exit 1
      fi
      run_agent reservations
      run_agent reserve-batch
      run_agent stock
      ;;
    duplicate_delivery)
      if run_agent provision nina@example.test pro --key provision-nina; then
        echo "Expected duplicate-delivery fault did not occur" >&2; exit 1
      fi
      run_agent operations
      run_agent provision nina@example.test pro --key provision-nina
      run_agent provision omar@example.test starter --key provision-omar
      run_agent accounts
      ;;
  esac
  "${compose[@]}" exec -T -u root main mkdir -p /state /tests
  tmpdb="$(mktemp -u)"
  "${compose[@]}" cp trustval-api:/state/trustval.db "$tmpdb"
  "${compose[@]}" cp "$tmpdb" main:/state/trustval.db
  rm -f "$tmpdb"
  "${compose[@]}" cp "$task/tests/verify.py" main:/tests/verify.py
  "${compose[@]}" exec -T -u root main python /tests/verify.py
  reward="$("${compose[@]}" exec -T -u root main cat /logs/verifier/reward.json)"
  printf '%s' "$reward" | python -c 'import json,sys; r=json.load(sys.stdin); assert r["task_success"] == 1.0, r'
  echo "END-TO-END API + verifier OK: $name"
  cleanup
  trap - EXIT
done
