# Source Provenance and Reuse Audit

## Original author's exact MIT code — imported, no modifications
- Author: Vuk Rosić.
- Source: https://github.com/vukrosic/llm-research-paper-drafts
- Immutable source commit: **d0dc052749a97061f6daa6907371bd0a2ec33405** (Nov 16, 2026).
- Original directory: 02-muon-hypergradient-learning-rate/.
- Imported untouched: vendor/vukrosic/{ss.py,drive.py,theory_check.py}; preserve copied vendor/vukrosic/LICENSE (MIT) and copyright.
- ss.py is a monolithic argparse-driven tiny Transformer, Muon and hypergradient experiment; NOT a reusable RL optimizer package. It reads data/fineweb_train_000001.slice and data/fineweb_val_000000.slice at import, not supplied in original folder, and fixes torch seed 0.
- drive.py wraps ss.py using Unix nice and expects local FineWeb slices; theory_check.py is an independent NumPy-only finite-difference check. Full original replication **not completed**.

## Better actual RL starting point — not wholesale copied
**Primary:** https://github.com/OPTML-Group/Pion/tree/87965014b360bde604632cba0aa12e423c6c63c6/RL/verl. This FSDP2-aware fork provides MuonAdamW, PerHeadMuonAdamW, DefaultPionAdamW and PerHeadPionAdamW, plus AdamW and native GRPO/GMPO recipes; inspect Apache-2.0 and upstream notices before porting.

**Secondary agentic:** https://github.com/x66ccff/verl-muon/tree/6692817d594d45af8558f719261edde14fcb63b2. Contains MuonWithAdamW in verl/utils/optim.py, ALFWorld launchers and update-RMS instrumentation. Contains Apache-2.0-derived verl/verl-agent components with third-party notices. The reference Muon integration uses FSDP NO_SHARD, creating potentially prohibitive GPU memory requirements. Do not blindly port.

## Reuse discipline
Use the original author controller as a reference only after validating independent finite differences and securing legitimate FineWeb data if replication is desired. For real policy training, select ONE fixed trainer revision and use its existing optimizer code; do not mix implementations across two forks into a purported matched comparison. A hypergradient port, if later chosen, must identify exact diff, license, optimizer routing, group/step scheduling, and independent tests. Record all upstream SHAs and change provenance in experiment handoff.

## Current claims
We have imported reference code and written a planned comparison. No model run, reproducing result, gradient diagnostic on actual RL gradients, or paper submission has occurred.
