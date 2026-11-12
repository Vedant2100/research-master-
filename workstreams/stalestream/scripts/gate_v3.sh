#!/usr/bin/env bash
# Gate v3 (relative / cross-referenced dates). Run from workstreams/stalestream.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1
RAW=$S/data/episodes_v3_raw
V3=$S/data/episodes_v3
R=$S/runs/gate_v3
MQ=$S/data/MQuAKE-CF-3k-v2.json
mkdir -p "$V3" "$R"
cp $RAW/value_aliases.json $RAW/meta.json $V3/
log() { echo "[$(date +%T)] $*" | tee -a $R/progress.log; }

lane_a() {  # GPU 0
  for sp in test val; do
    CUDA_VISIBLE_DEVICES=0 python -m stalestream.paraphrase --episodes $RAW/$sp.jsonl --out $V3/$sp.jsonl >|"$R/para_$sp.log" 2>&1
    log "A: paraphrased $sp $(grep -E '^\{"lines' $R/para_$sp.log)"
  done
  for sp in val test; do
    CUDA_VISIBLE_DEVICES=0 python -m stalestream.extract --episodes $V3/$sp.jsonl --mquake $MQ \
      --out $R/extract_$sp.jsonl >|"$R/extract_$sp.log" 2>&1
    log "A: extract_rules(4B) $sp $(grep -E '^\{"lines' $R/extract_$sp.log)"
    for m in 1.7B 4B; do
      CUDA_VISIBLE_DEVICES=0 python -m stalestream.writer --episodes $V3/$sp.jsonl --model Qwen/Qwen3-$m \
        --arm prompted_${m,,} --out $R/writer_${m,,}_$sp.jsonl >|"$R/writer_${m,,}_$sp.log" 2>&1
    done
    log "A: prompted 1.7B/4B $sp done"
  done
  touch $R/.lane_a_eval_ready
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.paraphrase --episodes $RAW/train_2s.jsonl --out $V3/train_2s.jsonl >|"$R/para_train.log" 2>&1
  log "A: paraphrased train $(grep -E '^\{"lines' $R/para_train.log)"
}

lane_b() {  # GPU 1
  until grep -q '^{"lines' $R/para_test.log 2>/dev/null; do sleep 20; done
  until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 1)" -lt 2000 ]; do sleep 60; done
  CUDA_VISIBLE_DEVICES=1 python -m stalestream.judge --raw $RAW/test.jsonl --para $V3/test.jsonl --n 400 \
    --out $R/judge_test_flagged.jsonl >|"$R/judge.log" 2>&1
  log "B: judge $(grep -E '^\{"judged' $R/judge.log)"
  for ctx in header session; do
    arm=extract_rules_32b; [ $ctx = session ] && arm=extract_rules_32b_ctx
    CUDA_VISIBLE_DEVICES=1 python -m stalestream.extract --episodes $V3/test.jsonl --mquake $MQ --model Qwen/Qwen3-32B-AWQ \
      --gpu-mem 0.93 --context $ctx --arm $arm --out $R/$arm.jsonl >|"$R/$arm.log" 2>&1
    log "B: $arm test $(grep -E '^\{"lines' $R/$arm.log)"
  done
  CUDA_VISIBLE_DEVICES=1 python -m stalestream.writer --episodes $V3/test.jsonl --model Qwen/Qwen3-32B-AWQ \
    --arm prompted_32b --gpu-mem 0.93 --max-len 3072 --out $R/writer_32b_test.jsonl >|"$R/writer_32b_test.log" 2>&1
  log "B: prompted 32B test done"
}

lane_a &
PA=$!
lane_b
until [ -f $R/.lane_a_eval_ready ]; do sleep 30; done
BASE="oracle no_memory write_all newest_wins symbolic bm25 extract_rules prompted_1.7b prompted_4b"
CUDA_VISIBLE_DEVICES=1 python -m stalestream.reader --episodes $V3/val.jsonl --aliases $V3/value_aliases.json --mquake $MQ \
  --arms $BASE --memories $R/extract_val.jsonl --memories $R/writer_1.7b_val.jsonl --memories $R/writer_4b_val.jsonl \
  --out $R/eval_val.jsonl >|"$R/eval_val.log" 2>&1
log "reader val: $(tail -12 $R/eval_val.log | tr -d '\n ')"
CUDA_VISIBLE_DEVICES=1 python -m stalestream.reader --episodes $V3/test.jsonl --aliases $V3/value_aliases.json --mquake $MQ \
  --arms $BASE extract_rules_32b extract_rules_32b_ctx prompted_32b --memories $R/extract_test.jsonl \
  --memories $R/writer_1.7b_test.jsonl --memories $R/writer_4b_test.jsonl --memories $R/extract_rules_32b.jsonl \
  --memories $R/extract_rules_32b_ctx.jsonl --memories $R/writer_32b_test.jsonl --out $R/eval_test.jsonl >|"$R/eval_test.log" 2>&1
log "reader test: $(tail -15 $R/eval_test.log | tr -d '\n ')"
B=""; for a in no_memory write_all newest_wins symbolic bm25 extract_rules prompted_1.7b prompted_4b extract_rules_32b extract_rules_32b_ctx prompted_32b; do B="$B --baseline $a"; done
python headroom_gate.py $R/eval_test.jsonl $B >|$R/gate_test.json || true
log "GATE: $(python -c "import json;d=json.load(open('$R/gate_test.json'));print(d['oracle'],d['strongest_nonprivileged_baseline'],d['oracle_minus_strongest'],d['paired_bootstrap_gap_95_percent'],'PASS' if d['pass'] else 'FAIL')")"
wait $PA
log "GATE V3 DONE"
