# StaleStream

**Track:** Memory & Continual Learning  
**Canonical source (private):** https://github.com/Vedant2100/StaleStream  
**Status:** Implemented and executed; research comparison still in progress  
**Priority:** HIGH — complete a fair post-training comparison and reproducibility package

## Research question

Can an RL-trained system maintain bounded external memory across sequential sessions when facts become stale, conflict, arrive out of order, use aliases, or require temporal/source reasoning?

## Verified results (latest status: 2026-11-15)

- **v3 environment gate: marginal pass.** Oracle test EM 0.997; strongest non-privileged baseline, 32B session-context extraction plus rules, 0.783; gap 0.214 with paired-bootstrap 95% CI [0.194, 0.234]. The point estimate passes the fixed 0.20 threshold, but the interval crosses it.
- **GRPO writer:** 1.7B model, three seeds, test EM 0.292 ± 0.026 versus 0.211 untrained.
- **GRPO extractor:** 1.7B model, three seeds, test EM 0.691 ± 0.011 versus 0.259 untrained.
- **Date-driven conflict resolution:** after correcting the broken date metric, GRPO `winner_ok` rises from about 0.69 to 0.83 (header context) / 0.85 (session context).
- **Held-out reader:** gains transfer to Phi-3.5; the extractor and writer improvements are not limited to the Qwen3 reward reader.

## Limitations and claim guardrails

- The 32B session-context extraction-plus-rules baseline still outperforms the trained 1.7B extractor.
- Initial extractor DPO/RFT results are one seed each; the comparison is not yet a fair algorithm ranking. Validation-only tuning, iterative/on-policy DPO and multi-seed evaluation remain open.
- The v3 gate is marginal, not an unqualified pass: its confidence interval crosses the threshold.
- This is evidence in a controlled memory-maintenance environment, not proof of general-purpose agent memory, parameter-level continual learning, or recursive self-improvement.
- Raw run traces remain on the original BCC scratch filesystem; the standalone repository contains code and aggregate evidence, not the complete trace bundle.

## Next decisive actions

1. Tune DPO on validation only; keep test untouched.
2. Run iterative/on-policy DPO with the same frozen reader reward and compare against three-seed GRPO.
3. Replicate the selected RFT setting across seeds if compute permits.
4. Preserve the corrected date/conflict diagnostics and evaluate per-tag memory correctness.
5. Export and verify reproducible per-seed traces and manifests.

See the [canonical STATUS.md](https://github.com/Vedant2100/StaleStream/blob/main/STATUS.md), [README](https://github.com/Vedant2100/StaleStream), and [research next-steps plan](https://github.com/Vedant2100/StaleStream/blob/main/NEXT_STEPS_2026-11-14.md).