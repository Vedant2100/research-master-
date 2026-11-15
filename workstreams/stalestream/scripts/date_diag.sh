#!/usr/bin/env bash
# Date-metric fix (2026-11-15): re-extract the test split with --dump for every extractor arm, then score
# date accuracy per kind against stream-resolved gold dates (stalestream.dates). Diagnostic only: no
# training, no reader. Run from workstreams/stalestream.
set -uo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1
D=$S/data/episodes_v3; MQ=$S/data/MQuAKE-CF-3k-v2.json
R=$S/runs/date_diag; mkdir -p "$R"
R1=$S/runs/main_v3_grpo_extract; R2=$S/runs/extractor_round2
log() { echo "[$(date +%T)] $*" | tee -a "$R/progress.log"; }

run() {  # gpu name model context [extra]
  [ -s $R/dump_$2.jsonl ] && return
  CUDA_VISIBLE_DEVICES=$1 python -m stalestream.extract --episodes $D/test.jsonl --mquake $MQ --model $3 --context $4 ${5:-} \
    --arm $2 --out $R/mem_$2.jsonl --dump $R/dump_$2.jsonl >|"$R/$2.log" 2>&1 && log "done $2" || log "FAILED $2"
}

( run 0 base Qwen/Qwen3-1.7B header
  run 0 base_ctx Qwen/Qwen3-1.7B session
  run 0 c_base Qwen/Qwen3-1.7B header --constrained
  for s in 0 1 2; do run 0 hdr_s$s $R1/ext_s$s/final header; done
  for s in 0 1 2; do run 0 ctx_s$s $R2/ctx_s$s/final session; done
  run 0 rft $R2/rft/final header
  run 0 dpo $R2/dpo/final header ) &
( run 1 32b_ctx Qwen/Qwen3-32B-AWQ session "--gpu-mem 0.93"
  run 1 32b Qwen/Qwen3-32B-AWQ header "--gpu-mem 0.93"
  run 1 4b_ctx Qwen/Qwen3-4B session ) &
wait
ARGS=""; for f in $R/dump_*.jsonl; do n=$(basename $f .jsonl); ARGS="$ARGS --dump ${n#dump_}=$f"; done
python -m stalestream.diag --episodes $D/test.jsonl --mquake $MQ $ARGS --out $R/diag_test.jsonl >|"$R/diag.log" 2>&1 && log "DIAG DONE" || log "DIAG FAILED"
