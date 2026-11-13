# Proof Is Not Truth (AI × Epistemics)

**Track:** Model Epistemics & Trust Infrastructure (Apart Sprint November 13–15, 2026)  
**Source:** `workstreams/proof-is-not-truth/`  
**State:** HARNESS VALIDATED, LIVE QWEN2.5-7B PILOT EXECUTED  
**Decision:** ACTIVE (Apart Sprint Workstream)

## Research question
Do independently verified provenance signals improve the factual decisions of tool-using LLM agents, and when might they create misplaced trust in authentic but false information?

## Experimental evidence structure
1. **Pre-sprint audit (Nov 6–7):** ProvenanceTrap on Qwen2.5-3B had a 78.9% competence floor (60/76 failures quit on step 1); apparent safety (0 unauthorized writes) was an illusion caused by agent paralysis. No genuine cryptographic tooling existed.
2. **Deterministic harness validation:** 192 simulated episodes verifying that the HMAC-SHA256 keystore, path-traversal isolation, telemetry engine, and deterministic state graders execute without runtime errors. Confirms simulator behavior across hand-coded archetypes.
3. **Live Qwen2.5-7B real-model evaluation:** Live open-weights LLM running in-cluster without access to ground-truth labels. Evaluated across 5 conditions:
   - `no_metadata`: Plain context baseline.
   - `textual_authority`: Prominent text authority claims.
   - `verified_origin`: Cryptographic HMAC-SHA256 provenance verification (no telemetry).
   - `telemetry_only`: Independent telemetry corroboration (no provenance) to isolate causal impact.
   - `corroborated_provenance`: Decoupled origin verification with live telemetry corroboration and explicit abstention.

## Methods / comparisons
Five matched conditions with matched step budgets ($N \le 5$), genuine HMAC-SHA256 detached manifests, and real environment state scoring. Model prompts strictly exclude ground-truth split and correctness labels.

## Limitations and unproven claims
Evaluated on Qwen2.5-7B-Instruct. Generalization to proprietary frontier models (e.g., GPT-4o, Claude 3.5 Sonnet) requires multi-model sweeps.

See [Literature & Audit](../workstreams/proof-is-not-truth/LITERATURE_AND_AUDIT.md), [Sprint Report](../workstreams/proof-is-not-truth/reports/APART_RESEARCH_REPORT.md), and [Status](../workstreams/proof-is-not-truth/STATUS.md).
