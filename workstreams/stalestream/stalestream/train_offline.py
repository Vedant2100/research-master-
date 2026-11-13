"""Offline training from the sample bank: RFT (supervised on best candidates) or DPO (best vs
worst candidate for the same prompt). Full fine-tuning, no LoRA, one A30:
fp32 master weights with bf16 autocast, 8-bit AdamW, gradient checkpointing. DPO precomputes
reference log-probs, so no reference model is held in memory during training.

  python -m stalestream.train_offline --mode rft --data bank/rft.jsonl --out runs/rft
  python -m stalestream.train_offline --mode dpo --data bank/dpo.jsonl --out runs/dpo
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["rft", "dpo"], required=True)
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-1.7B")
    ap.add_argument("--lr", type=float, default=None, help="default 5e-6 (rft) / 1e-6 (dpo)")
    ap.add_argument("--epochs", type=float, default=None, help="default 2 (rft) / 1 (dpo)")
    ap.add_argument("--beta", type=float, default=0.1)
    ap.add_argument("--batch", type=int, default=2)
    ap.add_argument("--grad-accum", type=int, default=8)
    ap.add_argument("--max-length", type=int, default=2048)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    import torch
    from datasets import load_dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32)
    keep = ["prompt", "completion"] if args.mode == "rft" else ["prompt", "chosen", "rejected"]
    ds = load_dataset("json", data_files=str(args.data), split="train")
    ds = ds.remove_columns([c for c in ds.column_names if c not in keep])
    common = dict(output_dir=str(args.out), per_device_train_batch_size=args.batch,
                  gradient_accumulation_steps=args.grad_accum, bf16=True, gradient_checkpointing=True,
                  optim="adamw_bnb_8bit", lr_scheduler_type="cosine", warmup_ratio=0.05, logging_steps=5,
                  save_strategy="no", report_to=[], seed=args.seed, max_length=args.max_length)
    if args.mode == "rft":
        from trl import SFTConfig, SFTTrainer
        cfg = SFTConfig(learning_rate=args.lr or 5e-6, num_train_epochs=args.epochs or 2,
                        completion_only_loss=True, packing=False, **common)
        trainer = SFTTrainer(model=model, args=cfg, train_dataset=ds, processing_class=tok)
    else:
        from trl import DPOConfig, DPOTrainer
        cfg = DPOConfig(learning_rate=args.lr or 1e-6, num_train_epochs=args.epochs or 1, beta=args.beta,
                        precompute_ref_log_probs=True, **common)
        trainer = DPOTrainer(model=model, args=cfg, train_dataset=ds, processing_class=tok)
    trainer.train()
    final = args.out / "final"
    trainer.model.to(torch.bfloat16).save_pretrained(final)
    tok.save_pretrained(final)
    print(f"saved {final}")


if __name__ == "__main__":
    main()
