#!/usr/bin/env bash
# Timing + smoke test of GRPO on the extractor (grpo_extract.py), then a check that the extract.py
# refactor reproduces the size-matched 1.7B header-context extraction byte-for-byte. Run from workstreams/stalestream.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
D=$S/data/episodes_v3
R=$S/runs/grpo_extract_timing
MQ=$S/data/MQuAKE-CF-3k-v2.json
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
CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_extract --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
  --mquake $MQ --steps ${STEPS:-15} --out $R/run >|"$R/run.log" 2>&1 || log "TRAIN FAILED"
log "train done: $(tail -1 $R/run/train_log.jsonl 2>/dev/null)"
kill $WS $RS; wait $WS $RS 2>/dev/null || true; trap - EXIT; sleep 10
CUDA_VISIBLE_DEVICES=0 python -m stalestream.extract --episodes $D/test.jsonl --mquake $MQ --model Qwen/Qwen3-1.7B \
  --arm extract_rules_1.7b --out $R/refactor_check.jsonl >|"$R/refactor_check.log" 2>&1
cmp -s $R/refactor_check.jsonl $S/runs/size_matched_v3/extract_rules_1.7b_test.jsonl && log "REFACTOR IDENTICAL" || log "REFACTOR DIFFERS"
log "TIMING DONE"
