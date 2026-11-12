#!/usr/bin/env bash
# Gate v3 rerun after the extraction output-cap fix (160 -> 1024 tokens). Reuses the v3 data,
# paraphrases, judge result and prompted 1.7B/4B writer outputs from gate_v3.sh.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1
V3=$S/data/episodes_v3
R=$S/runs/gate_v3
MQ=$S/data/MQuAKE-CF-3k-v2.json
log() { echo "[$(date +%T)] $*" | tee -a $R/progress.log; }
log "RERUN after extraction cap fix (max_tokens 1024)"

gpu0() {
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.extract --episodes $V3/test.jsonl --mquake $MQ --model Qwen/Qwen3-32B-AWQ \
    --gpu-mem 0.93 --context header --arm extract_rules_32b --out $R/extract_rules_32b.jsonl >|"$R/extract_rules_32b.log" 2>&1
  log "G0: extract_rules_32b test $(grep -E '^\{"lines' $R/extract_rules_32b.log)"
  for sp in val test; do
    CUDA_VISIBLE_DEVICES=0 python -m stalestream.extract --episodes $V3/$sp.jsonl --mquake $MQ \
      --out $R/extract_$sp.jsonl >|"$R/extract_$sp.log" 2>&1
    log "G0: extract_rules(4B) $sp $(grep -E '^\{"lines' $R/extract_$sp.log)"
  done
}
gpu1() {
  CUDA_VISIBLE_DEVICES=1 python -m stalestream.extract --episodes $V3/test.jsonl --mquake $MQ --model Qwen/Qwen3-32B-AWQ \
    --gpu-mem 0.93 --context session --arm extract_rules_32b_ctx --out $R/extract_rules_32b_ctx.jsonl >|"$R/extract_rules_32b_ctx.log" 2>&1
  log "G1: extract_rules_32b_ctx test $(grep -E '^\{"lines' $R/extract_rules_32b_ctx.log)"
  CUDA_VISIBLE_DEVICES=1 python -m stalestream.writer --episodes $V3/test.jsonl --model Qwen/Qwen3-32B-AWQ \
    --arm prompted_32b --gpu-mem 0.93 --max-len 3072 --out $R/writer_32b_test.jsonl >|"$R/writer_32b_test.log" 2>&1
  log "G1: prompted 32B test done"
}
gpu0 & P0=$!
gpu1 & P1=$!
wait $P0; wait $P1

BASE="oracle no_memory write_all newest_wins symbolic bm25 extract_rules prompted_1.7b prompted_4b"
CUDA_VISIBLE_DEVICES=0 python -m stalestream.reader --episodes $V3/val.jsonl --aliases $V3/value_aliases.json --mquake $MQ \
  --arms $BASE --memories $R/extract_val.jsonl --memories $R/writer_1.7b_val.jsonl --memories $R/writer_4b_val.jsonl \
  --out $R/eval_val.jsonl >|"$R/eval_val.log" 2>&1 &
PV=$!
CUDA_VISIBLE_DEVICES=1 python -m stalestream.reader --episodes $V3/test.jsonl --aliases $V3/value_aliases.json --mquake $MQ \
  --arms $BASE extract_rules_32b extract_rules_32b_ctx prompted_32b --memories $R/extract_test.jsonl \
  --memories $R/writer_1.7b_test.jsonl --memories $R/writer_4b_test.jsonl --memories $R/extract_rules_32b.jsonl \
  --memories $R/extract_rules_32b_ctx.jsonl --memories $R/writer_32b_test.jsonl --out $R/eval_test.jsonl >|"$R/eval_test.log" 2>&1
wait $PV
log "reader val: $(tail -12 $R/eval_val.log | tr -d '\n ')"
log "reader test: $(tail -15 $R/eval_test.log | tr -d '\n ')"
B=""; for a in no_memory write_all newest_wins symbolic bm25 extract_rules prompted_1.7b prompted_4b extract_rules_32b extract_rules_32b_ctx prompted_32b; do B="$B --baseline $a"; done
python headroom_gate.py $R/eval_test.jsonl $B >|$R/gate_test.json || true
log "GATE: $(python -c "import json;d=json.load(open('$R/gate_test.json'));print(d['oracle'],d['strongest_nonprivileged_baseline'],d['oracle_minus_strongest'],d['paired_bootstrap_gap_95_percent'],'PASS' if d['pass'] else 'FAIL')")"
log "GATE V3 DONE"
