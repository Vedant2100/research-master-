# RL Optimizer Geometry — Noisy-Gradient Post-Training

**Track:** RL Post-Training & Reward Design  
**Agent:** rl-optimizer-geometry  
**Stage:** INCUBATION / CODE-SOURCED, no RL runs  
**Priority:** CONDITIONAL — preflight and diagnostic first  
**Issue:** https://github.com/Vedant2100/research-master-/issues/22

## Question
When does matrix-aware optimization help versus destabilize RL post-training under low-quality, sparse or nonstationary gradients? Can same-policy gradient statistics predict optimizer failures on held-out tasks after controlling learning rate, update magnitude, KL, clipping, and reward construction?

## Scope
The target is **scientific understanding of optimizer geometry** (AdamW, Muon, Pion), not simply copying the author's Muon scheduler. Rosić reports small-model LM results, Fan et al. report Muon failure/Pion benefit in RLVR, and Ruan et al. report Muon benefit in some agentic-RL recipes. These are separate settings and not a contradiction without experimental matching. ISO, MuonMax and GRPO gradient-rank studies are important competing prior art.

## Sources
- Verbatim, MIT-licensed tiny-LM hypergradient source: [vendor](../workstreams/rl-optimizer-geometry/vendor/vukrosic/README.md), commit d0dc052749a97061f6daa6907371bd0a2ec33405. Not an RL trainer; missing FineWeb slice data.
- Primary future RL stack: official [Pion RL/verl](https://github.com/OPTML-Group/Pion/tree/87965014b360bde604632cba0aa12e423c6c63c6/RL/verl) with AdamW/Muon/Pion in one FSDP2-aware implementation.
- Optional secondary agentic transfer: [verl-muon](https://github.com/x66ccff/verl-muon/tree/6692817d594d45af8558f719261edde14fcb63b2) for ALFWorld. Its FSDP NO_SHARD choice is an important VRAM constraint.

## Decision
Worth a CPU diagnostic and audited experimental preflight; not an authorized large GPU campaign. Need competent non-saturated base, fair optimizer tuning, same-data matched-budget comparisons, at least 3 independent training seeds and held-out diagnostic success before claiming improvement or proposing a new algorithm. Stop when tuned AdamW/update-RMS controls explain the gap. No submissions or GPU spend without approval.

See [research plan](../workstreams/rl-optimizer-geometry/RESEARCH_PLAN.md), [literature](../workstreams/rl-optimizer-geometry/LITERATURE.md), [reuse audit](../workstreams/rl-optimizer-geometry/UPSTREAM_REUSE.md), and [status](../workstreams/rl-optimizer-geometry/STATUS.md).
