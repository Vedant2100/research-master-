#!/usr/bin/env bash
# Full fine-tuning GRPO timing test (HANDOFF item 7). Run from workstreams/stalestream.
# GPU 1: writer sampler (weight transfer) + reader. GPU 0: trainer.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
D=${DATA:-$S/data/episodes_v1}
ALGO=${ALGO:-grpo}
R=$S/runs/full_ft_timing${TAG:-}
mkdir -p "$R"
log() { echo "[$(date +%T)] $*"; }

# Start the two GPU-1 servers one after the other: concurrent startup makes vLLM's memory
# profiling count the other process's allocations and the second engine fails to get KV cache.
wait_up() {  # port pid
  until curl -sf http://127.0.0.1:$1/v1/models >/dev/null; do
    kill -0 $2 2>/dev/null || { log "server on $1 died"; exit 1; }; sleep 3; done
}
WMEM=0.30; RMEM=0.50
[ "$ALGO" = opsd_frozen ] && { WMEM=0.28; RMEM=0.42; }
WS=""
if curl -sf http://127.0.0.1:8402/v1/models >/dev/null; then
  log "reusing writer server already on 8402"
else
  VLLM_SERVER_DEV_MODE=1 CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-1.7B --port 8402 \
    --weight-transfer-config '{"backend": "nccl"}' --gpu-memory-utilization $WMEM --max-model-len 4096 \
    >|"$R/writer_server.log" 2>&1 &
  WS=$!
fi
trap 'kill ${WS:-} ${RS:-} 2>/dev/null || true' EXIT
[ -n "$WS" ] && wait_up 8402 $WS
CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --gpu-memory-utilization $RMEM \
  --max-model-len 2048 >|"$R/reader_server.log" 2>&1 &
RS=$!
wait_up 8401 $RS
TS=""
if [ "$ALGO" = opsd_frozen ]; then  # frozen teacher = initial writer weights, never synced
  CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-1.7B --port 8403 --gpu-memory-utilization 0.18 \
    --max-model-len 4096 --max-logprobs 20 >|"$R/teacher_server.log" 2>&1 &
  TS=$!
  wait_up 8403 $TS
fi
trap 'kill ${WS:-} ${RS:-} ${TS:-} 2>/dev/null || true' EXIT
log "servers up"

# OPSD: same 32 trajectories per step as GRPO, as 32 episodes x 1 sample (no groups needed)
EXTRA=""; { [ "$ALGO" = opsd ] || [ "$ALGO" = opsd_frozen ]; } && EXTRA="--episodes-per-step 32 --group 1"
CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_full --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
  --steps ${STEPS:-20} --algo $ALGO --beta 0 $EXTRA --out $R/${ALGO}_beta0 >|"$R/${ALGO}_beta0.log" 2>&1
log "${ALGO} beta0 done"
if [ "${KL_TEST:-0}" = 1 ]; then
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_full --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
    --steps 5 --algo grpo --beta 0.01 --out $R/beta001 >|"$R/beta001.log" 2>&1
  log "beta001 done"
fi
log "TIMING DONE"
