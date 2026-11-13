#!/usr/bin/env bash
# GRPO seeds (default 1 2) on v3, identical to main run 1 except the seed; final checkpoint; val + test eval.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
D=$S/data/episodes_v3
R=$S/runs/main_v3_grpo_seeds
MQ=$S/data/MQuAKE-CF-3k-v2.json
SEEDS=${SEEDS:-"1 2"}
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
for SEED in $SEEDS; do
  log "train grpo seed $SEED"
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_full --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
    --steps 300 --algo grpo --beta 0 --seed $SEED --save --out $R/grpo_s$SEED >|"$R/grpo_s$SEED.log" 2>&1
  log "train grpo seed $SEED done"
done
kill $WS $RS; wait $WS $RS 2>/dev/null || true; trap - EXIT; sleep 10
for SEED in $SEEDS; do
  for sp in val test; do
    G=0; [ $sp = test ] && G=1
    ( CUDA_VISIBLE_DEVICES=$G python -m stalestream.writer --episodes $D/$sp.jsonl --model $R/grpo_s$SEED/final \
        --arm grpo_300_s$SEED --out $R/mem_s${SEED}_$sp.jsonl >|"$R/mem_s${SEED}_$sp.log" 2>&1 && \
      CUDA_VISIBLE_DEVICES=$G python -m stalestream.reader --episodes $D/$sp.jsonl --aliases $D/value_aliases.json \
        --mquake $MQ --arms grpo_300_s$SEED --memories $R/mem_s${SEED}_$sp.jsonl --out $R/eval_s${SEED}_$sp.jsonl \
        >|"$R/eval_s${SEED}_$sp.log" 2>&1 ) &
  done
  wait
  for sp in val test; do log "eval seed $SEED $sp: $(tail -3 $R/eval_s${SEED}_$sp.log | tr -d '\n ')"; done
done
log "SEEDS DONE"
