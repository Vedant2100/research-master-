#!/usr/bin/env bash
# Main run 1 on v3: full-FT GRPO and OPSD, 300 steps, seed 0, final checkpoint, val + test eval.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
D=$S/data/episodes_v3
R=$S/runs/main_v3_run1
MQ=$S/data/MQuAKE-CF-3k-v2.json
STEPS=${STEPS:-300}
mkdir -p "$R"
log() { echo "[$(date +%T)] $*" | tee -a $R/progress.log; }
wait_up() { until curl -sf http://127.0.0.1:$1/v1/models >/dev/null; do kill -0 $2 2>/dev/null || { log "server $1 died"; exit 1; }; sleep 3; done; }

VLLM_SERVER_DEV_MODE=1 CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-1.7B --port 8402 \
  --weight-transfer-config '{"backend": "nccl"}' --gpu-memory-utilization 0.30 --max-model-len 4096 >|"$R/writer_server.log" 2>&1 &
WS=$!
trap 'kill $WS ${RS:-} 2>/dev/null || true' EXIT
wait_up 8402 $WS
CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --gpu-memory-utilization 0.50 --max-model-len 2048 >|"$R/reader_server.log" 2>&1 &
RS=$!
wait_up 8401 $RS
log "servers up"

for ALGO in grpo opsd; do
  EXTRA=""; [ $ALGO = opsd ] && EXTRA="--episodes-per-step 32 --group 1"
  log "train $ALGO $STEPS steps"
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_full --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
    --steps $STEPS --algo $ALGO --beta 0 --seed 0 $EXTRA --save --out $R/$ALGO >|"$R/$ALGO.log" 2>&1
  log "train $ALGO done"
done
kill $WS $RS; wait $WS $RS 2>/dev/null || true; trap - EXIT
sleep 10

for ALGO in grpo opsd; do
  for sp in val test; do
    G=0; [ $sp = test ] && G=1
    CUDA_VISIBLE_DEVICES=$G python -m stalestream.writer --episodes $D/$sp.jsonl --model $R/$ALGO/final \
      --arm ${ALGO}_300 --out $R/${ALGO}_mem_$sp.jsonl >|"$R/${ALGO}_mem_$sp.log" 2>&1 &
  done
  wait
done
log "writer eval done"
for sp in val test; do
  G=0; [ $sp = test ] && G=1
  CUDA_VISIBLE_DEVICES=$G python -m stalestream.reader --episodes $D/$sp.jsonl --aliases $D/value_aliases.json --mquake $MQ \
    --arms grpo_300 opsd_300 --memories $R/grpo_mem_$sp.jsonl --memories $R/opsd_mem_$sp.jsonl \
    --out $R/eval_$sp.jsonl >|"$R/eval_$sp.log" 2>&1 &
done
wait
for sp in val test; do log "reader $sp: $(tail -4 $R/eval_$sp.log | tr -d '\n ')"; done
log "RUN1 DONE"
