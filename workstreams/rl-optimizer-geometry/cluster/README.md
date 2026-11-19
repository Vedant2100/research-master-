# Cluster runs (free, 2 GPUs)

`setup.sh` runs once on the login node, CPU only. It clones Pion at the pinned SHA and rebuilds `verl/trainer/config/data/legacy_data.yaml`, which Pion's `**/data/` gitignore rule dropped. It then prepares GSM8K, caches Qwen3-1.7B and re-runs the Modal preflight sanity checks inside the same image. Everything goes under `$ROG`, which defaults to `$HOME/rog`. `/scratch` cannot be used because it is local to the login node and the compute nodes can't see it.

`probe.sbatch` runs the official recipe for `STEPS` steps (default 3) with no validation and no checkpoints:

    sbatch --export=ALL,OPT=muon workstreams/rl-optimizer-geometry/cluster/probe.sbatch

For a correctness-only smoke run on a 24 GB card, set `EXTRA` to extra Hydra overrides, such as smaller micro-batches or `data.train_batch_size=32`.

Workarounds baked into the probe:
- The model loads from its local snapshot path. transformers 4.57.3 calls the Hub API for a Hub model id (a Mistral regex check) even with `HF_HUB_OFFLINE=1`.
- The trailing `/` is stripped from that path because verl asserts against it.
- Ray's temp dir is node-local `/tmp`, because Ray's Unix sockets misbehave on NFS.
- The `DataLoader worker ... killed` traceback at the end of a run is shutdown noise. It appears after the last step has logged.

`pilot.sbatch` runs one full official run (105 steps, validation every 5) for `OPT=adamw|muon|pion`:

    for o in adamw muon pion; do sbatch --export=ALL,OPT=$o --output=$HOME/rog/logs/pilot-$o-%j.out workstreams/rl-optimizer-geometry/cluster/pilot.sbatch; done

The jobs share the `fm-serial` name with `singleton`, so only one runs at a time (the 2-GPU cap). On 2× RTX 6000 Ada a step takes ~20 min, so a run takes ~36 h. The recipe is unchanged except:
- logging goes to a JSONL file at `$ROG/pilot/$OPT.jsonl` instead of wandb;
- the model loads from the local snapshot (same workarounds as the probe);
- `data.seed=1`. The recipe leaves it null, which gives every run an unseeded shuffle. Pinning it gives all three optimizers the same data order and keeps the order across resumes;
- checkpoints go to `$ROG/ckpt/$OPT`, keeping only the latest (each is ~20–30 GB with optimizer state). Resubmitting the same `OPT` resumes from it (`resume_mode=auto`) and appends to the same JSONL.
