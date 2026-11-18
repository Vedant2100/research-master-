"""Modal cost probe for the official Pion GRPO recipes (Qwen3-1.7B, GSM8K, 2 GPUs).

Two entry modes:
    modal run .../cost_probe.py --mode preflight   # CPU only: env, data, model, configs, optimizers
    modal run .../cost_probe.py --mode probe       # GPU: a few training steps to measure step time

The probe runs examples/grpo_trainer/run_qwen3-1.7b_fsdp2_<opt>.sh from OPTML-Group/Pion at a
pinned commit, unchanged except: data path, no wandb, no checkpoints, capped steps, and one
validation at the last step. It measures timing/cost only; it is not a result.
"""
import modal

PION_SHA = "87965014b360bde604632cba0aa12e423c6c63c6"
VERL = "/opt/Pion/RL/verl"
# Official verl image with vLLM 0.12 (verl 0.7 moved to vllm==0.12.0; this fork is verl 0.8.0.dev).
# The fork README's torch 2.6 instructions predate its own code, which imports vLLM >=0.11 APIs.
VERL_IMAGE = "verlai/verl@sha256:9576682f85ca36f4ef719efccc5a5deb4d0b6f66f06fc14f43fdfed0749fbf5d"
DATA = "/cache/data/gsm8k"
MODEL = "Qwen/Qwen3-1.7B"
RECIPES = {
    "adamw": "examples/grpo_trainer/run_qwen3-1.7b_fsdp2_adamw.sh",
    "muon": "examples/grpo_trainer/run_qwen3-1.7b_fsdp2_muon.sh",
    "pion": "examples/grpo_trainer/run_qwen3-1.7b_fsdp2_pion.sh",
}

image = (
    modal.Image.from_registry(VERL_IMAGE)
    .run_commands(
        "git clone https://github.com/OPTML-Group/Pion.git /opt/Pion",
        f"cd /opt/Pion && git checkout {PION_SHA}",
        f"cd {VERL} && pip install --no-deps -e .",
        # Pion's .gitignore has `**/data/`, which dropped verl/trainer/config/data/legacy_data.yaml from
        # the fork, so ppo_trainer.yaml cannot compose. Rebuild it from the fork's own fully composed
        # reference (_generated_ppo_trainer.yaml); upstream verl's file has drifted from this fork.
        f"cd {VERL}/verl/trainer/config && mkdir -p data && python3 -c \"import yaml; "
        "d = yaml.safe_load(open('_generated_ppo_trainer.yaml'))['data']; "
        "yaml.safe_dump(d, open('data/legacy_data.yaml', 'w'), sort_keys=False)\"",
        # Point every recipe at the volume copy of GSM8K.
        f"cd {VERL} && sed -i 's#\\$HOME/data/gsm8k#{DATA}#g' examples/grpo_trainer/run_qwen3-1.7b_fsdp2_*.sh",
    )
    .env({"HF_HOME": "/cache/hf", "TOKENIZERS_PARALLELISM": "false", "WANDB_MODE": "disabled"})
)

app = modal.App("rog-cost-probe", image=image)
cache = modal.Volume.from_name("rog-cache", create_if_missing=True)


def recipe_overrides(name: str) -> list[str]:
    """Hydra overrides exactly as written in the pinned recipe script (PROMOTION_STEPS default 0)."""
    import shlex
    text = open(f"{VERL}/{RECIPES[name]}").read().replace("${PROMOTION_STEPS}", "0")
    body = text.split("verl.trainer.main_ppo", 1)[1].split("$@", 1)[0]
    return [t for t in shlex.split(body.replace("\\\n", " ")) if "=" in t]


PROBE_OVERRIDES = ["trainer.logger=['console','file']", "trainer.save_freq=-1", "trainer.val_before_train=False"]


def parse_metrics(jsonl_text: str) -> dict:
    import json
    steps, val_s, acc = {}, [], []
    for line in jsonl_text.splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        d = rec["data"]
        if "timing_s/step" in d:
            steps[rec["step"]] = float(d["timing_s/step"]) - float(d.get("timing_s/testing", 0.0))
        if "timing_s/testing" in d:
            val_s.append(float(d["timing_s/testing"]))
        for k, v in d.items():
            if k.startswith("val-core/openai/gsm8k/") and "mean@" in k:
                acc.append(float(v))
    return {"train_step_s": steps, "val_s": val_s, "val_acc": acc}


@app.function(cpu=4, memory=16 * 1024, volumes={"/cache": cache}, timeout=40 * 60)
def preflight() -> list[tuple[str, bool, str]]:
    import importlib, os, subprocess, sys, traceback
    results = []

    def check(name, fn):
        try:
            msg = fn()
            results.append((name, True, str(msg or "")))
        except Exception as e:  # report every check, don't stop at the first failure
            results.append((name, False, f"{type(e).__name__}: {e}\n{traceback.format_exc()[-1500:]}"))
        print(("PASS " if results[-1][1] else "FAIL ") + name + " :: " + results[-1][2][:400], flush=True)

    os.chdir(VERL)
    sys.path.insert(0, VERL)

    def versions():
        out = {}
        for m in ["torch", "vllm", "flash_attn", "transformers", "ray", "tensordict", "numpy", "verl", "orjson"]:
            mod = importlib.import_module(m)
            out[m] = getattr(mod, "__version__", "?")
        import torch, verl
        assert verl.__file__.startswith(VERL), f"verl imported from {verl.__file__}, not the Pion fork"
        assert torch.version.cuda, "torch has no CUDA build"
        return out
    check("versions + verl comes from Pion fork", versions)

    check("pip check", lambda: subprocess.run([sys.executable, "-m", "pip", "check"],
                                              capture_output=True, text=True).stdout[-1500:] or "clean")

    def imports():
        for m in ["verl.trainer.main_ppo", "verl.trainer.ppo.ray_trainer", "verl.workers.fsdp_workers",
                  "verl.workers.rollout.vllm_rollout.vllm_async_server", "verl.workers.rollout.vllm_rollout.vllm_rollout",
                  "verl.utils.reward_score.gsm8k", "verl.third_party.vllm"]:
            importlib.import_module(m)
        from verl.utils import muon
        for c in ["MuonAdamW", "DefaultPionAdamW"]:
            assert hasattr(muon, c), c
        import flash_attn.bert_padding  # noqa: F401  used by use_remove_padding
        return "all import"
    check("imports (trainer, FSDP workers, vLLM async rollout, muon)", imports)

    def data():
        import pandas as pd
        if not os.path.exists(f"{DATA}/train.parquet"):
            subprocess.run([sys.executable, "examples/data_preprocess/gsm8k.py", "--local_dir", DATA], check=True)
            cache.commit()
        tr, te = pd.read_parquet(f"{DATA}/train.parquet"), pd.read_parquet(f"{DATA}/test.parquet")
        assert len(tr) == 7473 and len(te) == 1319, (len(tr), len(te))
        for col in ["data_source", "prompt", "reward_model"]:
            assert col in tr.columns, col
        assert set(tr.data_source) == {"openai/gsm8k"}
        assert all(str(r["ground_truth"]).strip() for r in tr.reward_model)
        return f"train={len(tr)} test={len(te)}; steps/epoch={len(tr)//1024}, 15 epochs={15*(len(tr)//1024)} steps"
    check("GSM8K parquet", data)

    def model():
        from huggingface_hub import snapshot_download
        from transformers import AutoConfig, AutoTokenizer
        import pandas as pd
        path = snapshot_download(MODEL)
        cache.commit()
        cfg = AutoConfig.from_pretrained(path)
        assert (cfg.num_attention_heads, cfg.num_key_value_heads, cfg.hidden_size) == (16, 8, 2048), cfg
        tok = AutoTokenizer.from_pretrained(path)
        lens = []
        for split in ["train", "test"]:
            for p in pd.read_parquet(f"{DATA}/{split}.parquet").prompt:
                ids = tok.apply_chat_template(list(p), add_generation_prompt=True, tokenize=True)
                lens.append(len(ids))
        assert max(lens) <= 512, f"prompt over max_prompt_length: {max(lens)}"
        return f"tie_word_embeddings={cfg.tie_word_embeddings}; max prompt tokens={max(lens)} (limit 512)"
    check("Qwen3-1.7B download + prompt lengths", model)

    def reward():
        from verl.utils.reward_score import gsm8k
        assert gsm8k.compute_score("reasoning ... #### 72", "72") == 1.0
        assert gsm8k.compute_score("reasoning ... #### 71", "72") == 0.0
        assert gsm8k.compute_score("no final answer", "72") == 0.0
        return "correct=1, wrong=0, missing=0"
    check("GSM8K reward function", reward)

    from hydra import compose, initialize_config_dir
    from omegaconf import OmegaConf
    configs = {}

    def default_matches_generated():
        import yaml
        with initialize_config_dir(config_dir=f"{VERL}/verl/trainer/config", version_base=None):
            base = OmegaConf.to_container(compose(config_name="ppo_trainer"), resolve=False)
        gen = yaml.safe_load(open(f"{VERL}/verl/trainer/config/_generated_ppo_trainer.yaml"))
        base.pop("model_engine", None)  # Hydra defaults selector, stripped from the generated file
        assert base == gen, "composed default config differs from the fork's _generated_ppo_trainer.yaml"
        return "identical"
    check("restored legacy_data.yaml: default config == fork's generated reference", default_matches_generated)

    def compose_all():
        from verl.utils.config import validate_config
        out = []
        for name in RECIPES:
            ov = recipe_overrides(name) + PROBE_OVERRIDES + ["trainer.total_training_steps=3", "trainer.test_freq=-1"]
            with initialize_config_dir(config_dir=f"{VERL}/verl/trainer/config", version_base=None):
                cfg = compose(config_name="ppo_trainer", overrides=ov)
            validate_config(config=cfg, use_reference_policy=True, use_critic=False)
            a = cfg.actor_rollout_ref
            assert a.model.path == MODEL and cfg.data.train_files == f"{DATA}/train.parquet"
            assert cfg.trainer.n_gpus_per_node == 2 and a.rollout.tensor_model_parallel_size == 2
            OmegaConf.resolve(cfg)  # catch bad interpolations now, not on the GPU
            configs[name] = cfg
            out.append(f"{name}: {a.actor.optim.optimizer_impl}.{a.actor.optim.optimizer} lr={a.actor.optim.lr}")
        return "; ".join(out)
    check("Hydra compose + verl validate_config for adamw/muon/pion", compose_all)

    def optimizers():
        import torch
        from transformers import Qwen3Config, Qwen3ForCausalLM
        from verl.utils.config import omega_conf_to_dataclass
        from verl.workers.config.optimizer import FSDPOptimizerConfig, build_optimizer
        assert set(configs) == set(RECIPES), f"no composed config for {set(RECIPES) - set(configs)}"
        out = []
        for name, cfg in configs.items():
            torch.manual_seed(0)
            tiny = Qwen3Config(vocab_size=256, hidden_size=64, intermediate_size=128, num_hidden_layers=2,
                               num_attention_heads=4, num_key_value_heads=2, head_dim=16, tie_word_embeddings=True)
            m = Qwen3ForCausalLM(tiny)
            raw = OmegaConf.to_container(cfg.actor_rollout_ref.actor.optim, resolve=True)
            raw["lr"] = 1e-3  # recipe lr 1e-6 is too small to see a change on a tiny model; dataclass is frozen
            ocfg = omega_conf_to_dataclass(OmegaConf.create(raw), dataclass_type=FSDPOptimizerConfig)
            opt = build_optimizer(m.named_parameters(), ocfg)
            before = {n: p.detach().clone() for n, p in m.named_parameters()}
            ids = torch.randint(0, 256, (2, 16))
            m(input_ids=ids, labels=ids).loss.backward()
            opt.step()
            changed = [n for n, p in m.named_parameters() if not torch.equal(before[n], p)]
            assert len(changed) == len(before), f"unchanged: {set(before) - set(changed)}"
            assert all(torch.isfinite(p).all() for p in m.parameters())
            groups = [(g.get("use_muon"), len(g["params"])) for g in opt.param_groups]
            if name != "adamw":
                muon_ids = {id(p) for g in opt.param_groups if g.get("use_muon") for p in g["params"]}
                for n, p in m.named_parameters():
                    should = p.ndim >= 2 and "embed" not in n and "lm_head" not in n
                    assert (id(p) in muon_ids) == should, f"{name}: {n} routed wrong"
            out.append(f"{name}: {type(opt).__name__} groups={groups}")
        return "; ".join(out)
    check("build_optimizer + one CPU step, routing embed/norms->AdamW", optimizers)

    def parser():
        import orjson
        line = orjson.dumps({"step": 4, "data": {"timing_s/step": 130.5, "timing_s/testing": 30.5,
                             "val-core/openai/gsm8k/reward/mean@1": 0.7}}, option=orjson.OPT_SERIALIZE_NUMPY)
        r = parse_metrics(line.decode())
        assert r == {"train_step_s": {4: 100.0}, "val_s": [30.5], "val_acc": [0.7]}, r
        return r
    check("metrics parser on FileLogger-format JSONL", parser)

    def recipes_patched():
        for name, path in RECIPES.items():
            t = open(f"{VERL}/{path}").read()
            assert "$HOME/data" not in t and DATA in t, name
        return "data path rewritten in all 3"
    check("recipe data paths", recipes_patched)

    def memory_estimate():
        n = 1.72e9
        # fp32 master params + grads, sharded across 2 GPUs; states: AdamW 2, Muon/Pion 1 (momentum).
        per = {k: n * 4 * (2 + s) / 2 / 1e9 for k, s in {"adamw": 2, "muon": 1, "pion": 1}.items()}
        vllm = 0.6 * 48
        return {k: f"train state ~{v:.1f} GB/GPU (+activations); vLLM reserves {vllm:.0f} GB but sleeps during update"
                for k, v in per.items()}
    check("rough per-GPU memory on 48 GB L40S", memory_estimate)

    return results


def _probe(opt: str = "muon", steps: int = 3) -> dict:
    import os, subprocess, time
    log_path = f"/cache/probe/{opt}_{int(time.time())}.jsonl"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    # Frugal: no validation in the probe (val is ~1319 short rollouts, estimated from rollout timing instead).
    overrides = PROBE_OVERRIDES + [f"trainer.total_training_steps={steps}", "trainer.test_freq=-1"]
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="0,1", VERL_FILE_LOGGER_PATH=log_path)
    t0 = time.time()
    p = subprocess.run(["bash", RECIPES[opt], *overrides], cwd=VERL, env=env)
    wall = time.time() - t0
    cache.commit()
    m = parse_metrics(open(log_path).read()) if os.path.exists(log_path) else {}
    return {"exit": p.returncode, "wall_s": round(wall), **m}


import os as _os

# The GPU function is only registered when asked for (ROG_GPU=1), so the CPU preflight
# can run on an account without GPU billing enabled.
if not modal.is_local() or _os.environ.get("ROG_GPU") == "1":
    probe = app.function(gpu="L40S:2", volumes={"/cache": cache}, timeout=35 * 60, cpu=8,
                         memory=64 * 1024, name="probe")(_probe)


@app.local_entrypoint()
def main(mode: str = "preflight", opt: str = "muon", steps: int = 3):
    if mode == "preflight":
        res = preflight.remote()
        bad = [r for r in res if not r[1]]
        print(f"\n{len(res) - len(bad)}/{len(res)} checks passed")
        for name, ok, msg in res:
            print(("PASS" if ok else "FAIL"), name, "::", msg[:2000])
        if bad:
            raise SystemExit(1)
    else:
        assert _os.environ.get("ROG_GPU") == "1", "set ROG_GPU=1 to run the GPU probe"
        r = probe.remote(opt, steps)
        print(r)
