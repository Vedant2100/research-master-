#!/usr/bin/env bash
# Go/no-go pilot: one full official run (105 steps, val every 5) of one optimizer on 2 GPUs.
# Recipe is unchanged except logging (file JSONL instead of wandb), checkpoint location/retention,
# and the model path (local snapshot; see probe.sbatch). Resubmitting the same OPT resumes from the
# last checkpoint (trainer.resume_mode=auto) and appends to the same JSONL.
#   for o in adamw muon pion; do sbatch --export=ALL,OPT=$o workstreams/rl-optimizer-geometry/cluster/pilot.sbatch; done
# All jobs share the fm-serial name + singleton, so they run one at a time (2-GPU cap).
# Measured on 2x RTX 6000 Ada: ~20 min/step -> ~36 h per run.
#SBATCH --job-name=fm-serial
#SBATCH --partition=gpu
#SBATCH --gres=gpu:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=2-12:00:00
#SBATCH --dependency=singleton
#SBATCH --output=/home/csgrad/%u/rog/logs/pilot-%x-%j.out
set -euo pipefail
ROG=${ROG:-$HOME/rog}
OPT=${OPT:?set OPT=adamw|muon|pion}
VERL=$ROG/Pion/RL/verl
LOG=$ROG/pilot/${OPT}.jsonl
CKPT=$ROG/ckpt/$OPT
MODEL=$(ls -d "$ROG"/hf/hub/models--Qwen--Qwen3-1.7B/snapshots/*/ | head -1); MODEL=${MODEL%/}  # verl asserts no trailing slash
RAYTMP=/tmp/rog_ray_$SLURM_JOB_ID  # node-local: Ray sockets misbehave on NFS
mkdir -p "$ROG/pilot" "$CKPT" "$RAYTMP"
echo "OPT=$OPT job=$SLURM_JOB_ID node=$(hostname) start=$(date -Is)"
nvidia-smi --query-gpu=name,memory.total --format=csv
cd "$VERL"
apptainer exec --nv --cleanenv -B "$ROG" -B /tmp \
  --env HF_HOME="$ROG/hf",PYTHONPATH="$VERL",WANDB_MODE=disabled,TOKENIZERS_PARALLELISM=false,VERL_FILE_LOGGER_PATH="$LOG",RAY_TMPDIR="$RAYTMP",HF_HUB_OFFLINE=1 \
  "$ROG/verl.sif" bash "examples/grpo_trainer/run_qwen3-1.7b_fsdp2_${OPT}.sh" \
  "trainer.logger=['console','file']" "actor_rollout_ref.model.path=$MODEL" \
  "trainer.default_local_dir=$CKPT" trainer.max_actor_ckpt_to_keep=1 \
  "+ray_kwargs.ray_init._temp_dir=$RAYTMP" "ray_kwargs.ray_init.num_cpus=$SLURM_CPUS_PER_TASK"
echo "done $(date -Is) jsonl: $LOG"
rm -rf "$RAYTMP"
