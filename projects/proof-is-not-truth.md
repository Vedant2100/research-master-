# Proof Is Not Truth (AI × Epistemics)

**Track:** Trust Infrastructure / Model Epistemics (Apart AI × Epistemics Sprint, November 13–15, 2026)  
**Source:** `workstreams/proof-is-not-truth/`  
**State:** FULL 16-CASE × 6-CONDITION BENCHMARK COMPLETED (96 EPISODES ON QWEN2.5-7B; JOB #312727)  
**Decision:** DELIVERABLES COMPLETED & ARTIFACTS FINALIZED ON BRANCH

## Research question

When tool-using agents consume machine-verifiable provenance, do they distinguish origin authenticity from factual correctness when taking consequential actions, and can independent factual corroboration improve decisions without causing blanket abstention?

## Implemented architecture & protocol repairs

1. **Repaired Grader & Ground Truth Alignment (P0):**
   - AST/semantic execution grading for Python code targets and structural JSON comparison, resolving false negatives on multi-line equivalent code.
   - `valid_abstention` aligned strictly with `expected_decision == 'abstain'`; premature abstention on legitimate true tasks marked as failures.
   - Tool discovery via `list_telemetry_metrics()` providing metric names and descriptions while withholding live values until explicit query.
2. **Factorial 6-Condition Causal Isolation (P1):**
   - Condition 1: `no_metadata` (Zero metadata baseline)
   - Condition 2: `textual_authority` (Prose authority claims control)
   - Condition 3: `verified_origin` (HMAC-SHA256 MAC origin verification, no telemetry)
   - Condition 4: `telemetry_only` (Telemetry discovery & corroboration, no provenance)
   - Condition 5: `corroborated_provenance_neutral` (Provenance + Telemetry with neutral policy)
   - Condition 6: `corroborated_provenance_directive` (Provenance + Telemetry + explicit epistemic directive)
3. **Cryptographic Rigor:** Keyed HMAC-SHA256 MACs explicitly distinguished from asymmetric public-key digital signatures and action authorization.
4. **Active Full Suite Execution (P2):** Complete 16-case suite across 5 splits (`clean_baseline`, `authentic_true`, `unauth_false`, `authentic_false_trap`, `unauth_true`) executing live on `Qwen2.5-7B-Instruct`.

See [Next Steps and Validity Audit](../workstreams/proof-is-not-truth/NEXT_STEPS_2026-11-14.md), [Status](../workstreams/proof-is-not-truth/STATUS.md), and [Literature & Audit](../workstreams/proof-is-not-truth/LITERATURE_AND_AUDIT.md).
