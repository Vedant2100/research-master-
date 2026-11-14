#!/usr/bin/env bash
# Round-3 controls (preregistered in STATUS.md, 2026-11-14). Run from workstreams/stalestream.
# Waits for the round-2 driver (WAIT_PID) to exit, then in parallel:
#   GPU 0: constrained-decoding extraction (relation field limited to the label list), eval with the
#          training reader (Qwen3-4B): untrained 1.7B header/session context, header GRPO extractor s0.
#   GPU 1: held-out reader (Phi-3.5-mini-instruct, different family; never used for training or selection)
#          re-reads the saved memories of every v3 arm.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1
D=$S/data/episodes_v3; MQ=$S/data/MQuAKE-CF-3k-v2.json
R=$S/runs/round3_controls; mkdir -p "$R"
HR=${HELDOUT_READER:-microsoft/Phi-3.5-mini-instruct}
log() { echo "[$(date +%T)] $*" | tee -a "$R/progress.log"; }

if [ -n "${WAIT_PID:-}" ]; then
  log "waiting for PID $WAIT_PID"
  while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 60; done
fi
log "start"

constrained() {  # model arm context
  for sp in val test; do
    [ -s $R/eval_${2}_$sp.jsonl ] && continue
    CUDA_VISIBLE_DEVICES=0 python -m stalestream.extract --episodes $D/$sp.jsonl --mquake $MQ --model $1 --context $3 \
      --constrained --arm $2 --out $R/mem_${2}_$sp.jsonl >|"$R/mem_${2}_$sp.log" 2>&1
    CUDA_VISIBLE_DEVICES=0 python -m stalestream.reader --episodes $D/$sp.jsonl --aliases $D/value_aliases.json \
      --mquake $MQ --arms $2 --memories $R/mem_${2}_$sp.jsonl --out $R/eval_${2}_$sp.jsonl >|"$R/eval_${2}_$sp.log" 2>&1
    log "constrained $2 $sp: $(grep '^{"lines' $R/mem_${2}_$sp.log | cut -c1-220)"
  done
}

heldout() {  # re-read saved memories (arm names made unique) with the held-out reader
  for sp in val test; do
    [ -s $R/heldout_$sp.jsonl ] && continue
    python3 - "$S" "$sp" >|"$R/heldout_mem_$sp.jsonl" <<'EOF'
import json, sys, glob, os
S, sp = sys.argv[1:]
r = f"{S}/runs"
src = {  # new arm name: (file, arm in file or None)
  "base_1.7b": (f"{r}/size_matched_v3/eval_{sp}.jsonl", "extract_rules_1.7b"),
  "base_1.7b_ctx": (f"{r}/size_matched_v3/eval_{sp}.jsonl", "extract_rules_1.7b_ctx"),
  "4b_ctx": (f"{r}/size_matched_v3/eval_{sp}.jsonl", "extract_rules_4b_ctx"),
  "32b_ctx": (f"{r}/gate_v3/eval_{sp}.jsonl", "extract_rules_32b_ctx"),
  "32b": (f"{r}/gate_v3/eval_{sp}.jsonl", "extract_rules_32b"),
  "prompted_1.7b": (f"{r}/gate_v3/eval_{sp}.jsonl", "prompted_1.7b"),
  "writer_grpo_s0": (f"{r}/main_v3_run1/eval_grpo_{sp}.jsonl", None),
  "writer_grpo_s1": (f"{r}/main_v3_grpo_seeds/eval_s1_{sp}.jsonl", None),
  "writer_grpo_s2": (f"{r}/main_v3_grpo_seeds/eval_s2_{sp}.jsonl", None),
  "ext_rft": (f"{r}/extractor_round2/eval_rft_extract_{sp}.jsonl", None),
  "ext_dpo": (f"{r}/extractor_round2/eval_dpo_extract_{sp}.jsonl", None),
}
for s in range(3):
  src[f"ext_grpo_hdr_s{s}"] = (f"{r}/main_v3_grpo_extract/eval_s{s}_{sp}.jsonl", None)
  src[f"ext_grpo_ctx_s{s}"] = (f"{r}/extractor_round2/eval_grpo_extract_ctx_s{s}_{sp}.jsonl", None)
for name, (f, arm) in src.items():
  if not os.path.exists(f):
    print(f"missing {f}", file=sys.stderr); continue
  for l in open(f):
    x = json.loads(l)
    if arm is None or x["arm"] == arm:
      print(json.dumps({"episode_id": x["episode_id"], "arm": name, "memory": x["memory"]}))
EOF
    ARMS=$(python3 -c "import json,sys;print(' '.join(dict.fromkeys(json.loads(l)['arm'] for l in open(sys.argv[1]))))" $R/heldout_mem_$sp.jsonl)
    CUDA_VISIBLE_DEVICES=1 python -m stalestream.reader --episodes $D/$sp.jsonl --aliases $D/value_aliases.json \
      --mquake $MQ --model $HR --arms oracle no_memory write_all $ARMS --memories $R/heldout_mem_$sp.jsonl \
      --out $R/heldout_$sp.jsonl >|"$R/heldout_$sp.log" 2>&1
    log "heldout $sp: $(tail -40 $R/heldout_$sp.log | tr -d '\n ' | grep -o '{.*}' | cut -c1-600)"
  done
}

( constrained Qwen/Qwen3-1.7B c_base_1.7b header
  constrained Qwen/Qwen3-1.7B c_base_1.7b_ctx session
  constrained $S/runs/main_v3_grpo_extract/ext_s0/final c_grpo_hdr_s0 header ) &
A=$!
heldout &
B=$!
wait $A; wait $B
log "ROUND3 DONE"
