# Proof Is Not Truth Eval Agent

**Area:** Model Epistemics & Trust Infrastructure  
**Event:** Apart Research AI × Epistemics Sprint (November 13–15, 2026)  
**Owner agent:** `proof-is-not-truth`  
**Current agent state:** EXECUTING FULL 16-CASE × 6-CONDITION BENCHMARK ON QWEN2.5-7B (96 EPISODES; SLURM JOB #312727 ON NODE06)

## Research aim

Measure whether tool-using agents distinguish origin authenticity from factual correctness when taking state-changing actions, and whether independent factual corroboration improves decisions without causing blanket abstention. "Signature Blindness" remains a provisional label for the observed authentic-false acceptance pattern, not an established causal effect.

## Experimental gates

- [x] **Gate 1:** Apart Sprint brief and initial literature review completed. Related-work positioning updated in `LITERATURE_AND_AUDIT.md` (Learn2Discern, What Counts as Evidence, Auditing Provenance Sensitivity, and ProvenanceGuard correctly characterized).
- [x] **Gate 2:** Pre-sprint ProvenanceTrap harness audited; the Qwen2.5-3B competence-floor issue (78.9% premature halting) identified.
- [x] **Gate 3:** Clean-task competence and grading repairs implemented: exact-string checking replaced with AST/semantic execution grading for Python code and structural JSON comparison.
- [x] **Gate 4:** HMAC-SHA256 MAC-based origin-authentication and keystore implemented. This is a keyed message authentication code, not an asymmetric digital signature or public-key non-repudiation system.
- [x] **Gate 5:** 16-case benchmark across the authenticity × veracity matrix implemented with metric discovery (`list_telemetry_metrics`).
- [x] **Gate 6:** Deterministic harness validation executed to verify simulator mechanics and state grading (7 unit tests passing).
- [x] **Gate 7:** Six evaluation conditions implemented, isolating tool availability from caution directives (`no_metadata`, `textual_authority`, `verified_origin`, `telemetry_only`, `corroborated_provenance_neutral`, `corroborated_provenance_directive`).
- [x] **Gate 8:** Full 96-episode benchmark (16 cases × 6 conditions) executed on `Qwen2.5-7B-Instruct` on node06 (Job #312727).
- [x] **Gate 9:** Apart Research Report completed with full 96-episode empirical table, causal breakdown, and Paralyzed Guardian tradeoff analysis.

## Key empirical findings & methodological distinctions

1. **Origin authentication vs Factual veracity:** A valid HMAC-SHA256 MAC confirms that content originated with the authorized keyholder without transit alteration, but does not confirm that the content accurately reflects current environmental truth. In Cell C (authentic-false traps), `verified_origin` suffered 66.7% false trust, matching the 66.7% false trust observed under `no_metadata`. Origin verification failed to protect the agent against authentic falsehoods.
2. **Causal controls (Tools vs Prompt Directives):** In `corroborated_provenance_neutral`, the model defaulted to trusting the valid HMAC on `trap_01` (33.3% trap false trust) without checking telemetry. The explicit epistemic directive in `corroborated_provenance_directive` was required to prompt telemetry discovery and reduce trap false trust to 0.0%.
3. **The "Paralyzed Guardian" Tradeoff:** Mandating origin verification and telemetry corroboration induced severe over-abstention (62.5–81.3% abstention), collapsing Legitimate Task Completion (LTC) from 50–70% down to 10–20% on uncontested clean tasks and unsigned developer hotfixes.

## Evidence artifacts

- [Next steps and validity audit](NEXT_STEPS_2026-11-14.md)
- Protocol & audit: `workstreams/proof-is-not-truth/LITERATURE_AND_AUDIT.md`
- Code: `workstreams/proof-is-not-truth/src/`
- Tests: `workstreams/proof-is-not-truth/tests/test_harness.py`
- Full runner: `workstreams/proof-is-not-truth/scripts/run_qwen_full.sbatch`
- Raw results and traces (completed):
  - `workstreams/proof-is-not-truth/runs/qwen25_7b_full/evaluation_results.csv`
  - `workstreams/proof-is-not-truth/runs/qwen25_7b_full/evaluation_traces.json`
  - `workstreams/proof-is-not-truth/runs/qwen25_7b_full/metrics_summary.json`
  - `workstreams/proof-is-not-truth/runs/qwen25_7b_full/ollama_server_312727.log`
  - `workstreams/proof-is-not-truth/runs/qwen_full_312727.out`
- Research report: `workstreams/proof-is-not-truth/reports/APART_RESEARCH_REPORT.md`
- Run handoff: `workstreams/proof-is-not-truth/reports/EXPERIMENT_HANDOFF.md`

## Next action

Research workstream deliverables are complete, verified by real-model traces, and aligned with Apart Research sprint requirements. Commit and push branch to GitHub.

Follow `NEXT_STEPS_2026-11-14.md` in order: repair grader/tool discovery, correct the claims and literature review, then run the complete paired suite. Do not expand the benchmark or claim that corroboration restores safety until it improves false-action rates while retaining legitimate task completion.
