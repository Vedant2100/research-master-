# Proof Is Not Truth Eval Agent

**Area:** Model Epistemics & Trust Infrastructure  
**Event:** Apart Research AI × Epistemics Sprint (November 13–15, 2026)  
**Owner agent:** `proof-is-not-truth`  
**Current agent state:** EXECUTED PILOT, REPORT GENERATED, SUITE VERIFIED

## Research aim
Measure whether cryptographic provenance verification induces "Signature Blindness" (misplaced trust in authentic but false information) in tool-using agents, and demonstrate how independent factual corroboration and epistemic abstention restore safe decision-making.

## Experimental gates
- [x] **Gate 1:** Apart Sprint Brief and Literature Review (L2D 2607.19355, What Counts as Evidence 2610.12788, Auditing Provenance Sensitivity 2607.20827, ProvenanceGuard 2606.18037) completed.
- [x] **Gate 2:** Pre-sprint ProvenanceTrap harness audited; competence floor identified (78.9% premature halting).
- [x] **Gate 3:** Competence Gate established: 100% legitimate task completion on clean baseline tasks.
- [x] **Gate 4:** Genuine cryptographic provenance engine implemented (HMAC-SHA256 signatures and keystore; no fabricated labels).
- [x] **Gate 5:** 16-case benchmark across 2×2 epistemic matrix implemented.
- [x] **Gate 6:** Paired 192-episode pilot executed across 4 conditions with 3 seeds; raw CSV and traces preserved.
- [x] **Gate 7:** Apart-compliant research report authored with explicit prior-work disclosures.

## Key empirical findings
1. **Signature Blindness Confirmed:** Under Cell C (authentic origin but false claims), agents with verified origin metadata exhibit 100% false trust and 0% accuracy, mistaking cryptographic origin for factual truth.
2. **Epistemic Corroboration Resolves the Trap:** Equipping agents with independent telemetry corroboration and explicit abstention achieves 100% decision accuracy and 0% false trust.
3. **Verification Cost:** Achieving total epistemic safety requires only +1.0 tool call per episode over standard provenance checks.

## Evidence artifacts
- Protocol & Audit: `workstreams/proof-is-not-truth/LITERATURE_AND_AUDIT.md`
- Code Implementation: `workstreams/proof-is-not-truth/src/`
- Test Suite: `workstreams/proof-is-not-truth/tests/test_harness.py` (8/8 passing)
- Raw Traces & CSV: `workstreams/proof-is-not-truth/runs/pilot/`
- Research Report: `workstreams/proof-is-not-truth/reports/APART_RESEARCH_REPORT.md`
- Experiment Handoff: `workstreams/proof-is-not-truth/reports/EXPERIMENT_HANDOFF.md`
