#!/usr/bin/env bash
# One-time CPU setup on the login node for the cluster timing probe (mirrors modal/cost_probe.py's image).
# Clones Pion at the pinned SHA, restores the config file its .gitignore dropped, prepares GSM8K and
# caches Qwen3-1.7B. Everything lives under $ROG (default $HOME/rog: /scratch is node-local here, so use the shared NFS home).
set -euo pipefail
ROG=${ROG:-$HOME/rog}
SIF=$ROG/verl.sif
PION_SHA=87965014b360bde604632cba0aa12e423c6c63c6
VERL=$ROG/Pion/RL/verl
DATA=$ROG/data/gsm8k
export HF_HOME=$ROG/hf

[[ -f $SIF ]] || { echo "missing $SIF (apptainer pull it first)"; exit 1; }
if [[ ! -d $ROG/Pion ]]; then
  git clone -q https://github.com/OPTML-Group/Pion.git "$ROG/Pion"
fi
git -C "$ROG/Pion" checkout -q "$PION_SHA"
git -C "$ROG/Pion" diff --quiet -- RL/verl/examples || git -C "$ROG/Pion" checkout -q -- RL/verl/examples

run() { apptainer exec --cleanenv --env HF_HOME="$HF_HOME",PYTHONPATH="$VERL" -B "$ROG" "$SIF" "$@"; }

# Pion's `**/data/` gitignore rule dropped this file; rebuild it from the fork's generated reference.
mkdir -p "$VERL/verl/trainer/config/data"
run python3 -c "import yaml; d = yaml.safe_load(open('$VERL/verl/trainer/config/_generated_ppo_trainer.yaml'))['data']; yaml.safe_dump(d, open('$VERL/verl/trainer/config/data/legacy_data.yaml', 'w'), sort_keys=False)"
sed -i "s#\$HOME/data/gsm8k#$DATA#g" "$VERL"/examples/grpo_trainer/run_qwen3-1.7b_fsdp2_*.sh

[[ -f $DATA/train.parquet ]] || (cd "$VERL" && run python3 examples/data_preprocess/gsm8k.py --local_dir "$DATA")
run python3 -c "from huggingface_hub import snapshot_download; print(snapshot_download('Qwen/Qwen3-1.7B'))"

# Same sanity checks as the Modal preflight, inside the same image.
run python3 - <<EOF
import yaml, verl, pandas as pd
from hydra import compose, initialize_config_dir
from omegaconf import OmegaConf
assert verl.__file__.startswith("$VERL"), verl.__file__
tr, te = pd.read_parquet("$DATA/train.parquet"), pd.read_parquet("$DATA/test.parquet")
assert (len(tr), len(te)) == (7473, 1319)
with initialize_config_dir(config_dir="$VERL/verl/trainer/config", version_base=None):
    base = OmegaConf.to_container(compose(config_name="ppo_trainer"), resolve=False)
base.pop("model_engine", None)
assert base == yaml.safe_load(open("$VERL/verl/trainer/config/_generated_ppo_trainer.yaml"))
import verl.workers.rollout.vllm_rollout.vllm_async_server, verl.utils.muon  # noqa
print("setup OK: verl from fork, data 7473/1319, default config == generated reference")
EOF
grep -c "$DATA" "$VERL/examples/grpo_trainer/run_qwen3-1.7b_fsdp2_muon.sh"
