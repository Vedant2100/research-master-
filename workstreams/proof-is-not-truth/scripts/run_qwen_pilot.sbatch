#!/usr/bin/env bash
# Real-Model Evaluation Runner for 'Proof Is Not Truth'
# Runs Qwen2.5-7B via local Ollama container on csgrad compute node.
# Usage: sbatch scripts/run_qwen_pilot.sbatch

#SBATCH --job-name=pnt-qwen
#SBATCH --partition=batch
#SBATCH --cpus-per-task=16
#SBATCH --mem=32G
#SBATCH --time=00:30:00
#SBATCH --chdir=/home/csgrad/vbork001/research-master-
#SBATCH --output=/home/csgrad/vbork001/research-master-/workstreams/proof-is-not-truth/runs/qwen_pilot_%j.out

set -euo pipefail

REPO="/home/csgrad/vbork001/research-master-"
OLLAMA_SIF="/home/csgrad/vbork001/frontiermemory-experiment-20261024/containers/ollama.sif"
MODEL_STORE="/home/csgrad/vbork001/shared-mem-gov-pilot/models"
PORT="${PORT:-11588}"
OUT_DIR="${REPO}/workstreams/proof-is-not-truth/runs/qwen25_7b_pilot"

cd "$REPO"
mkdir -p "$OUT_DIR"

echo "=== Starting Ollama Server on $(hostname) on port ${PORT} ==="
apptainer exec --bind "${MODEL_STORE}:/models" \
  --env OLLAMA_MODELS=/models \
  --env OLLAMA_HOST=127.0.0.1:${PORT} \
  --env OLLAMA_NUM_PARALLEL=1 \
  "$OLLAMA_SIF" ollama serve > "${OUT_DIR}/ollama_server_${SLURM_JOB_ID}.log" 2>&1 &
SERVER_PID=$!
trap 'kill $SERVER_PID 2>/dev/null || true' EXIT

echo "Waiting for Ollama to become ready..."
for _ in $(seq 1 45); do
  if curl --fail --silent "http://127.0.0.1:${PORT}/api/tags" >/dev/null; then
    break
  fi
  sleep 1
done

echo "Ollama is ready. Preloading Qwen2.5-7B..."
curl --fail --silent "http://127.0.0.1:${PORT}/api/generate" -d '{"model": "qwen2.5:7b", "prompt": "", "keep_alive": "30m"}' >/dev/null

echo "=== Executing Real-Model Evaluation ==="
export PYTHONPATH="${REPO}/workstreams/proof-is-not-truth/src:${PYTHONPATH:-}"

python3 "${REPO}/workstreams/proof-is-not-truth/src/agent_eval.py" \
  --output-dir "$OUT_DIR" \
  --mode llm \
  --model "qwen2.5:7b" \
  --base-url "http://127.0.0.1:${PORT}/v1" \
  --temperature 0.0 \
  --seeds 42 \
  --quick-pilot

echo "=== Evaluation Finished Successfully ==="
