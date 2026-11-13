#!/usr/bin/env bash
# Main run 2 on v3: RFT + DPO (from the sample bank, in parallel on the two GPUs), then frozen-teacher OPSD.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
D=$S/data/episodes_v3
B=$S/runs/bank_v3
R=$S/runs/main_v3_run2
MQ=$S/data/MQuAKE-CF-3k-v2.json
mkdir -p "$R"
log() { echo "[$(date +%T)] $*" | tee -a $R/progress.log; }
wait_up() { until curl -sf http://127.0.0.1:$1/v1/models >/dev/null; do kill -0 $2 2>/dev/null || { log "server $1 died"; exit 1; }; sleep 3; done; }

evaluate() {  # arm model_dir
  for sp in val test; do
    G=0; [ $sp = test ] && G=1
    ( CUDA_VISIBLE_DEVICES=$G python -m stalestream.writer --episodes $D/$sp.jsonl --model $2 --arm $1 \
        --out $R/${1}_mem_$sp.jsonl >|"$R/${1}_mem_$sp.log" 2>&1 && \
      CUDA_VISIBLE_DEVICES=$G python -m stalestream.reader --episodes $D/$sp.jsonl --aliases $D/value_aliases.json \
        --mquake $MQ --arms $1 --memories $R/${1}_mem_$sp.jsonl --out $R/eval_${1}_$sp.jsonl >|"$R/eval_${1}_$sp.log" 2>&1 ) &
  done
  wait
  for sp in val test; do log "eval $1 $sp: $(tail -3 $R/eval_${1}_$sp.log | tr -d '\n ')"; done
}

log "train rft (GPU0) + dpo (GPU1)"
CUDA_VISIBLE_DEVICES=0 python -m stalestream.train_offline --mode rft --data $B/rft.jsonl --out $R/rft >|"$R/rft.log" 2>&1 &
P0=$!
CUDA_VISIBLE_DEVICES=1 python -m stalestream.train_offline --mode dpo --data $B/dpo.jsonl --out $R/dpo >|"$R/dpo.log" 2>&1 &
P1=$!
wait $P0; log "rft done"; wait $P1; log "dpo done"
evaluate rft $R/rft/final
evaluate dpo $R/dpo/final

VLLM_SERVER_DEV_MODE=1 CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-1.7B --port 8402 \
  --weight-transfer-config '{"backend": "nccl"}' --gpu-memory-utilization 0.30 --max-model-len 4096 >|"$R/writer_server.log" 2>&1 &
WS=$!
trap 'kill $WS ${RS:-} 2>/dev/null || true' EXIT
wait_up 8402 $WS
CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --gpu-memory-utilization 0.50 --max-model-len 2048 >|"$R/reader_server.log" 2>&1 &
RS=$!
wait_up 8401 $RS
log "servers up; train opsd_frozen 300 steps"
CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_full --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
  --steps ${STEPS:-300} --algo opsd_frozen --beta 0 --seed 0 --episodes-per-step 32 --group 1 --save \
  --out $R/opsd_frozen >|"$R/opsd_frozen.log" 2>&1
log "opsd_frozen done $(grep -c '"step"' $R/opsd_frozen/train_log.jsonl) steps; collapse_guard: $(grep -c collapse_guard $R/opsd_frozen.log || true)"
kill $WS $RS; wait $WS $RS 2>/dev/null || true; trap - EXIT; sleep 10
evaluate opsd_frozen_300 $R/opsd_frozen/final
log "RUN2 DONE"
