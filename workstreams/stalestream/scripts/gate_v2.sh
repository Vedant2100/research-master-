#!/usr/bin/env bash
# Gate v2 (HANDOFF items 2-6). Run from workstreams/stalestream after v2 raw episodes exist.
# Lane A (GPU 0): paraphrase val/test -> extract_rules -> prompted 1.7B/4B writers -> paraphrase train.
# Lane B (GPU 1): waits for paraphrased test -> 32B faithfulness judge -> prompted 32B writer.
# Then the reader scores every arm on val and test, and the gate runs on test.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1
RAW=$S/data/episodes_v2_raw
V2=$S/data/episodes_v2
R=$S/runs/gate_v2
MQ=$S/data/MQuAKE-CF-3k-v2.json
mkdir -p "$V2" "$R"
cp $RAW/value_aliases.json $RAW/meta.json $V2/
log() { echo "[$(date +%T)] $*"; }

lane_a() {
  for sp in test val; do
    CUDA_VISIBLE_DEVICES=0 python -m stalestream.paraphrase --episodes $RAW/$sp.jsonl --out $V2/$sp.jsonl \
      >|"$R/para_$sp.log" 2>&1
    log "A: paraphrased $sp $(grep -E '^\{"lines' $R/para_$sp.log)"
  done
  for sp in val test; do
    CUDA_VISIBLE_DEVICES=0 python -m stalestream.extract --episodes $V2/$sp.jsonl --mquake $MQ \
      --out $R/extract_$sp.jsonl >|"$R/extract_$sp.log" 2>&1
    log "A: extract_rules $sp $(grep -E '^\{"lines' $R/extract_$sp.log)"
    for m in 1.7B 4B; do
      CUDA_VISIBLE_DEVICES=0 python -m stalestream.writer --episodes $V2/$sp.jsonl --model Qwen/Qwen3-$m \
        --arm prompted_${m,,} --out $R/writer_${m,,}_$sp.jsonl >|"$R/writer_${m,,}_$sp.log" 2>&1
      log "A: prompted $m $sp done"
    done
  done
  CUDA_VISIBLE_DEVICES=0 python -m stalestream.paraphrase --episodes $RAW/train_2s.jsonl --out $V2/train_2s.jsonl \
    >|"$R/para_train.log" 2>&1
  log "A: paraphrased train $(grep -E '^\{"lines' $R/para_train.log)"
}

lane_b() {
  until [ -s $V2/test.jsonl ] && grep -q '^{"lines' $R/para_test.log 2>/dev/null; do sleep 20; done
  # GPU 1 must be free for the 32B model (a stale server may still hold it)
  until [ "$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits -i 1)" -lt 2000 ]; do
    log "B: waiting for GPU 1 to be free"; sleep 60; done
  CUDA_VISIBLE_DEVICES=1 python -m stalestream.judge --raw $RAW/test.jsonl --para $V2/test.jsonl --n 400 \
    --out $R/judge_test_flagged.jsonl >|"$R/judge.log" 2>&1
  log "B: judge $(grep -E '^\{"judged' $R/judge.log)"
  until [ -s $V2/val.jsonl ] && grep -q '^{"lines' $R/para_val.log 2>/dev/null; do sleep 20; done
  for sp in val test; do
    CUDA_VISIBLE_DEVICES=1 python -m stalestream.writer --episodes $V2/$sp.jsonl --model Qwen/Qwen3-32B-AWQ \
      --arm prompted_32b --gpu-mem 0.93 --max-len 3072 --out $R/writer_32b_$sp.jsonl >|"$R/writer_32b_$sp.log" 2>&1
    log "B: prompted 32B $sp done"
  done
}

lane_a > >(sed 's/^/  /') 2>&1 &
PA=$!
lane_b > >(sed 's/^/  /') 2>&1 &
PB=$!
wait $PB; log "lane B finished"
wait $PA; log "lane A finished"

for sp in val test; do
  CUDA_VISIBLE_DEVICES=1 python -m stalestream.reader --episodes $V2/$sp.jsonl --aliases $V2/value_aliases.json \
    --mquake $MQ --arms oracle no_memory write_all newest_wins symbolic bm25 extract_rules prompted_1.7b prompted_4b prompted_32b \
    --memories $R/extract_$sp.jsonl --memories $R/writer_1.7b_$sp.jsonl --memories $R/writer_4b_$sp.jsonl \
    --memories $R/writer_32b_$sp.jsonl --out $R/eval_$sp.jsonl >|"$R/eval_$sp.log" 2>&1
  log "reader $sp: $(tail -13 $R/eval_$sp.log | tr -d '\n ')"
done
python headroom_gate.py $R/eval_test.jsonl --baseline no_memory --baseline write_all --baseline newest_wins \
  --baseline symbolic --baseline bm25 --baseline extract_rules --baseline prompted_1.7b --baseline prompted_4b \
  --baseline prompted_32b >|$R/gate_test.json || true
log "GATE: $(python -c "import json;d=json.load(open('$R/gate_test.json'));print(d['oracle'],d['strongest_nonprivileged_baseline'],d['oracle_minus_strongest'],d['paired_bootstrap_gap_95_percent'],'PASS' if d['pass'] else 'FAIL')")"
log "GATE V2 DONE"
