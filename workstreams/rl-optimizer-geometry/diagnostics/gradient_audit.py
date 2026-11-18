"""CPU-only gradient diagnostic (not an optimizer or calibrated SNR estimate).

NPZ input: grad_a and grad_b, 2-D gradients from disjoint trajectory
microbatches at IDENTICAL frozen policy weights.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np


def summarize_pair(grad_a: np.ndarray, grad_b: np.ndarray) -> dict:
    a = np.asarray(grad_a, dtype=np.float64)
    b = np.asarray(grad_b, dtype=np.float64)
    if a.ndim != 2 or b.ndim != 2 or a.shape != b.shape or min(a.shape) == 0:
        raise ValueError("expected same-shaped nonempty 2-D gradient arrays")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise ValueError("gradients must be finite")
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    mean = (a + b) / 2
    singular = np.linalg.svd(mean, compute_uv=False)
    energies = singular ** 2
    total = float(energies.sum())
    cosine = float(np.sum(a * b) / (na * nb)) if na and nb else 0.0
    return {
        "rows": int(a.shape[0]), "cols": int(a.shape[1]),
        "split_half_cosine": max(-1.0, min(1.0, cosine)),
        "normalized_disagreement": float(np.linalg.norm(a - b)) / (na + nb) if (na + nb) else 0.0,
        "mean_gradient_norm": float(np.linalg.norm(mean)),
        "mean_gradient_stable_rank": float(total / energies[0]) if total else 0.0,
        "bottom_half_singular_energy_fraction": float(energies[len(energies)//2:].sum() / total) if total else 0.0
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True, type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    with np.load(a.input, allow_pickle=False) as data:
        metrics = summarize_pair(data["grad_a"], data["grad_b"])
    result = json.dumps(metrics, sort_keys=True, indent=2) + "\n"
    if a.output: a.output.write_text(result, encoding="utf-8")
    else: print(result, end="")


if __name__ == "__main__":
    main()
