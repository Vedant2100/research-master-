#!/usr/bin/env bash
# Size-matched extraction baselines on v3 (HANDOFF: size-matched framing). Run from workstreams/stalestream.
# GPU 0: Qwen3-1.7B extraction+rules, header and session context. GPU 1: Qwen3-4B session context.
set -euo pipefail
source /scratch/vbork001/stalestream/env.sh
export HF_HUB_OFFLINE=1
V3=$S/data/episodes_v3
R=$S/runs/size_matched_v3
MQ=$S/data/MQuAKE-CF-3k-v2.json
mkdir -p "$R"
log() { echo "[$(date +%T)] $*" | tee -a $R/progress.log; }

ext() {  # gpu model ctx arm split
  CUDA_VISIBLE_DEVICES=$1 python -m stalestream.extract --episodes $V3/$5.jsonl --mquake $MQ --model Qwen/Qwen3-$2 \
    --context $3 --arm $4 --out $R/${4}_$5.jsonl >|"$R/${4}_$5.log" 2>&1
  log "GPU$1: $4 $5 $(grep -E '^\{"lines' $R/${4}_$5.log)"
}
gpu0() { for sp in test val; do ext 0 1.7B header extract_rules_1.7b $sp; ext 0 1.7B session extract_rules_1.7b_ctx $sp; done; }
gpu1() { for sp in test val; do ext 1 4B session extract_rules_4b_ctx $sp; done; }
gpu0 & P0=$!
gpu1 & P1=$!
wait $P0; wait $P1

ARMS="extract_rules_1.7b extract_rules_1.7b_ctx extract_rules_4b_ctx"
for sp in test val; do
  g=0; [ $sp = val ] && g=1
  M=""; for a in $ARMS; do M="$M --memories $R/${a}_$sp.jsonl"; done
  CUDA_VISIBLE_DEVICES=$g python -m stalestream.reader --episodes $V3/$sp.jsonl --aliases $V3/value_aliases.json \
    --mquake $MQ --arms $ARMS $M --out $R/eval_$sp.jsonl >|"$R/eval_$sp.log" 2>&1 &
done
wait
for sp in test val; do log "reader $sp: $(tail -6 $R/eval_$sp.log | tr -d '\n ')"; done
log "SIZE MATCHED DONE"
