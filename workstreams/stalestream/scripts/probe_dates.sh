#!/usr/bin/env bash
# pass@N probe for relative / cross-referenced dates (val split). Waits for process group WAIT_PGID.
set -uo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1
D=$S/data/episodes_v3; MQ=$S/data/MQuAKE-CF-3k-v2.json; R=$S/runs/date_diag
log() { echo "[$(date +%T)] $*" | tee -a "$R/progress.log"; }
[ -n "${WAIT_PGID:-}" ] && while pgrep -g $WAIT_PGID >/dev/null; do sleep 30; done
probe() {  # gpu name model context
  CUDA_VISIBLE_DEVICES=$1 python -m stalestream.probe_dates --episodes $D/val.jsonl --mquake $MQ --model $3 --context $4 \
    --out $R/probe_$2.json >|"$R/probe_$2.log" 2>&1 && log "probe $2: $(cat $R/probe_$2.json)" || log "FAILED probe $2"
}
( probe 0 base_ctx Qwen/Qwen3-1.7B session; probe 0 ctx_s2 $S/runs/extractor_round2/ctx_s2/final session ) &
( probe 1 base_hdr Qwen/Qwen3-1.7B header; probe 1 4b_ctx Qwen/Qwen3-4B session ) &
wait; log "PROBE DONE"
