#!/usr/bin/env bash
# Extractor round 2 (preregistered 2026-11-13): (A) RFT + DPO on the extractor from a line-level bank of
# the base extractor; (B) GRPO extractor with session context, seeds 0 1 2. Run from workstreams/stalestream.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
D=$S/data/episodes_v3
R=$S/runs/extractor_round2
MQ=$S/data/MQuAKE-CF-3k-v2.json
mkdir -p "$R"
log() { echo "[$(date +%T)] $*" | tee -a $R/progress.log; }
wait_up() { until curl -sf http://127.0.0.1:$1/v1/models >/dev/null; do kill -0 $2 2>/dev/null || { log "server $1 died"; exit 1; }; sleep 3; done; }
evaluate() {  # gpu model arm context
  for sp in val test; do
    CUDA_VISIBLE_DEVICES=$1 python -m stalestream.extract --episodes $D/$sp.jsonl --mquake $MQ --model $2 --context $4 \
      --arm $3 --out $R/mem_${3}_$sp.jsonl >|"$R/mem_${3}_$sp.log" 2>&1
    CUDA_VISIBLE_DEVICES=$1 python -m stalestream.reader --episodes $D/$sp.jsonl --aliases $D/value_aliases.json \
      --mquake $MQ --arms $3 --memories $R/mem_${3}_$sp.jsonl --out $R/eval_${3}_$sp.jsonl >|"$R/eval_${3}_$sp.log" 2>&1
    log "eval $3 $sp: $(grep '^{"lines' $R/mem_${3}_$sp.log | cut -c1-200) EM=$(python3 -c "import json;r=[json.loads(l)['qa_exact_match'] for l in open('$R/eval_${3}_$sp.jsonl')];print(round(sum(r)/len(r),4))")"
  done
}

if [ "${SKIP_A:-0}" != 1 ]; then
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.bank_extract gen --episodes $D/train_2s.jsonl --mquake $MQ \
    --out $R/bank_raw.jsonl >|"$R/bank_gen.log" 2>&1
  log "bank gen: $(tail -1 $R/bank_gen.log)"
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.bank_extract score --bank $R/bank_raw.jsonl --episodes $D/train_2s.jsonl \
    --mquake $MQ --aliases $D/value_aliases.json --out $R/bank_scored.jsonl >|"$R/bank_score.log" 2>&1
  log "bank score: $(tail -1 $R/bank_score.log)"
  python -m stalestream.bank build --bank $R/bank_scored.jsonl --out-dir $R/bank --min-gap 0.16 --strict >|"$R/bank_build.log" 2>&1
  log "bank build: $(tail -1 $R/bank_build.log)"
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.train_offline --mode rft --data $R/bank/rft.jsonl --out $R/rft >|"$R/rft.log" 2>&1 &
  P0=$!
  CUDA_VISIBLE_DEVICES=1 python -m stalestream.train_offline --mode dpo --data $R/bank/dpo.jsonl --out $R/dpo >|"$R/dpo.log" 2>&1 &
  P1=$!
  wait $P0 && log "rft trained" || log "RFT FAILED"
  wait $P1 && log "dpo trained" || log "DPO FAILED"
  evaluate 0 $R/rft/final rft_extract header &
  evaluate 1 $R/dpo/final dpo_extract header &
  wait
fi

VLLM_SERVER_DEV_MODE=1 CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-1.7B --port 8402 \
  --weight-transfer-config '{"backend": "nccl"}' --gpu-memory-utilization 0.30 --max-model-len 4096 >|"$R/writer_server.log" 2>&1 &
WS=$!
trap 'kill $WS ${RS:-} 2>/dev/null || true' EXIT
wait_up 8402 $WS
CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --gpu-memory-utilization 0.50 --max-model-len 2048 >|"$R/reader_server.log" 2>&1 &
RS=$!
wait_up 8401 $RS
log "servers up"
for SEED in ${SEEDS:-0 1 2}; do
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo_extract --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
    --mquake $MQ --context session --steps ${STEPS:-200} --episodes-per-step 4 --lines-per-episode 64 --seed $SEED --save \
    --out $R/ctx_s$SEED >|"$R/ctx_s$SEED.log" 2>&1 || log "CTX SEED $SEED FAILED"
  log "ctx seed $SEED done: $(tail -1 $R/ctx_s$SEED/train_log.jsonl | cut -c1-160)"
done
kill $WS $RS; wait $WS $RS 2>/dev/null || true; trap - EXIT; sleep 10
evaluate 0 $R/ctx_s0/final grpo_extract_ctx_s0 session &
evaluate 1 $R/ctx_s1/final grpo_extract_ctx_s1 session &
wait
evaluate 0 $R/ctx_s2/final grpo_extract_ctx_s2 session
log "ROUND2 DONE"
