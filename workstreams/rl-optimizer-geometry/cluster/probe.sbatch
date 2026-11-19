#!/usr/bin/env bash
#SBATCH --job-name=fm-serial
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=00:45:00
#SBATCH --dependency=singleton
#SBATCH --output=/home/csgrad/%u/rog/logs/probe-%j.out
set -euo pipefail
ROG=${ROG:-$HOME/rog}
OPT=${OPT:-muon}
STEPS=${STEPS:-3}
EXTRA=${EXTRA:-}
VERL=$ROG/Pion/RL/verl
LOG=$ROG/probe/${OPT}_${SLURM_JOB_ID}.jsonl
MODEL=$(ls -d "$ROG"/hf/hub/models--Qwen--Qwen3-1.7B/snapshots/*/ | head -1); MODEL=${MODEL%/}
RAYTMP=/tmp/rog_ray_$SLURM_JOB_ID
mkdir -p "$ROG/probe" "$RAYTMP"
nvidia-smi --query-gpu=name,memory.total --format=csv
cd "$VERL"
apptainer exec --nv --cleanenv -B "$ROG" -B /tmp \
  --env HF_HOME="$ROG/hf",PYTHONPATH="$VERL",WANDB_MODE=disabled,TOKENIZERS_PARALLELISM=false,VERL_FILE_LOGGER_PATH="$LOG",RAY_TMPDIR="$RAYTMP",HF_HUB_OFFLINE=1 \
  "$ROG/verl.sif" bash "examples/grpo_trainer/run_qwen3-1.7b_fsdp2_${OPT}.sh" \
  "trainer.logger=['console','file']" trainer.save_freq=-1 trainer.val_before_train=False \
  "trainer.total_training_steps=$STEPS" trainer.test_freq=-1 "actor_rollout_ref.model.path=$MODEL" \
  "+ray_kwargs.ray_init._temp_dir=$RAYTMP" "ray_kwargs.ray_init.num_cpus=$SLURM_CPUS_PER_TASK" $EXTRA
echo "jsonl: $LOG"
python3 - "$LOG" <<'EOF'
import json, sys
for line in open(sys.argv[1]):
    r = json.loads(line); d = r["data"]
    keys = [k for k in d if k.startswith("timing_s/") or k.startswith("perf/max_memory") or k in ("critic/score/mean", "response_length/mean")]
    print("step", r["step"], {k: round(d[k], 2) for k in sorted(keys)})
EOF
