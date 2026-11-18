# RL Optimizer Geometry — Research Workstream

**Eleventh specialist, same four-track portfolio.** Scientific stage: design and code import, not executed or replicated RL evidence.

## Objective
Explain when gradient spectral geometry and independently sampled gradient disagreement predict RL post-training optimizer success/failure. Only develop an intervention after a successful held-out causal/diagnostic result.

## Navigate
- [Research hypothesis, preregistration and controls](RESEARCH_PLAN.md)
- [Fresh literature and novelty boundary](LITERATURE.md)
- [Pinned source code and licensing audit](UPSTREAM_REUSE.md)
- [Stage and blockers](STATUS.md)
- [Issue #22](https://github.com/Vedant2100/research-master-/issues/22)

## Reused code
The original author's MIT-licensed ss.py, drive.py, theory_check.py are imported **verbatim** into vendor/vukrosic/, pinned to upstream d0dc052749a97061f6daa6907371bd0a2ec33405. The standalone theory_check.py requires NumPy, but ss.py/drive.py need original FineWeb .slice files absent from the GitHub folder. Do not claim those original experiments were reproduced.

Our offline tool diagnostics/gradient_audit.py analyzes 2-D pre-update gradients from two independent microbatches sampled at identical policy weights. This is a heuristic diagnostic, **not a trained optimizer or validated SNR estimator**.

Run CPU tests from repository root:

    python -m unittest discover -s workstreams/rl-optimizer-geometry/tests -v

Run offline diagnostic (NPZ file contains grad_a and grad_b, each a same-shaped 2-D array):

    python workstreams/rl-optimizer-geometry/diagnostics/gradient_audit.py --input sample.npz

The primary **future** RL implementation is official Pion's RL/verl fork, which already provides AdamW/Muon/Pion. The secondary ALFWorld transfer is x66ccff/verl-muon. Those separate trainer forks are pinned references, not vendored or silently equated. No GPU runs initiated.
