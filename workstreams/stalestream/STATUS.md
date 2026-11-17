# StaleStream — coordination pointer

**Canonical repository (private):** https://github.com/Vedant2100/StaleStream  
**Canonical evidence:** https://github.com/Vedant2100/StaleStream/blob/main/STATUS.md  
**Project summary:** [projects/stalestream.md](../../projects/stalestream.md)

## Latest verified summary (2026-11-15)

- v3 gate: **marginal pass** — oracle 0.997, strongest non-privileged baseline 0.783, gap 0.214, paired-bootstrap 95% CI [0.194, 0.234].
- GRPO writer: 0.292 ± 0.026 test EM across three seeds, versus 0.211 untrained.
- GRPO extractor: 0.691 ± 0.011 test EM across three seeds, versus 0.259 untrained.
- Corrected date-driven conflict diagnostic: `winner_ok` improves from about 0.69 to 0.83–0.85.
- Held-out Phi-3.5 evaluation confirms positive transfer.
- The 32B session-context extraction-plus-rules pipeline remains stronger; DPO tuning and a fair multi-seed comparison remain open.

All code, detailed experiment records and future updates belong in the standalone repository. This file is only a coordination pointer; do not copy source code, hidden data, checkpoints or raw traces into this public master.
