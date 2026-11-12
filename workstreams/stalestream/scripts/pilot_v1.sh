#!/usr/bin/env bash
# v1 100-step GRPO and RLOO pilots + held-out evaluation. Run from workstreams/stalestream.
# Waits for any running v1 train paraphrase to finish first.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
D=$S/data/episodes_v1
R=$S/runs/pilot_v1
STEPS=${STEPS:-100}
mkdir -p "$R"
log() { echo "[$(date +%T)] $*"; }

while pgrep -f "python -m stalestream.paraphrase --episodes" >/dev/null; do sleep 30; done
python -c "
import json
from stalestream.generator import validate
eps=[json.loads(l) for l in open('$D/train_2s.jsonl')]
[validate(e) for e in eps]; print('train validated', len(eps))"
log "paraphrase done; $(grep -E '^\{"lines' $S/runs/para_v1_train.log)"

CUDA_VISIBLE_DEVICES=1 vllm serve Qwen/Qwen3-4B --port 8401 --max-model-len 2048 \
  --gpu-memory-utilization 0.85 >|"$R/reader_server.log" 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT
until curl -sf http://127.0.0.1:8401/v1/models >/dev/null; do
  kill -0 $SERVER 2>/dev/null || { log "reader server died"; exit 1; }; sleep 3; done
log "reader server up"

for ALGO in grpo rloo; do
  log "train $ALGO $STEPS steps"
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.grpo --episodes $D/train_2s.jsonl --aliases $D/value_aliases.json \
    --steps $STEPS --algo $ALGO --seed 0 --out $R/$ALGO >|"$R/$ALGO.log" 2>&1
  log "train $ALGO done"
done
kill $SERVER; wait $SERVER 2>/dev/null || true
trap - EXIT

for ALGO in grpo rloo; do
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.writer --episodes $D/test.jsonl --lora $R/$ALGO/adapter_final \
    --arm ${ALGO}_100 --out $R/${ALGO}_mem.jsonl >|"$R/${ALGO}_mem.log" 2>&1
done
log "writer eval done"
CUDA_VISIBLE_DEVICES=1 python -m stalestream.reader --episodes $D/test.jsonl --aliases $D/value_aliases.json \
  --mquake $S/data/MQuAKE-CF-3k-v2.json --arms grpo_100 rloo_100 \
  --memories $R/grpo_mem.jsonl --memories $R/rloo_mem.jsonl --out $R/trained_eval.jsonl >|"$R/trained_eval.log" 2>&1
cat $S/runs/v1_eval_all.jsonl $R/trained_eval.jsonl >|$R/all_eval.jsonl
log "PILOT DONE"
