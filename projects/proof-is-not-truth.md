# Proof Is Not Truth (AI × Epistemics)

**Track:** Model Epistemics & Trust Infrastructure (Apart Sprint November 13–15, 2026)  
**Source:** `workstreams/proof-is-not-truth/`  
**State:** EXECUTED PILOT, HYPOTHESIS CONFIRMED, CLEAN BASELINE ESTABLISHED  
**Decision:** ACTIVE (Apart Sprint Workstream)

## Research question
Do independently verified provenance signals improve the factual decisions of tool-using LLM agents, and when might they create misplaced trust in authentic but false information?

## Existing evidence
- **Pre-sprint audit (Nov 6–7):** ProvenanceTrap on Qwen2.5-3B had a 78.9% competence floor (60/76 failures quit on step 1); apparent safety (0 unauthorized writes) was an illusion caused by agent paralysis. No genuine cryptographic tooling existed.
- **Sprint pilot (Nov 13, 2026):** 192 paired episodes across 16 tasks and 4 conditions. Clean-task baseline achieved 100% legitimate task completion. In the "Proof Is Not Truth" trap (Cell C: authentic origin with factually corrupted claims), Condition 3 (verified origin) suffered 100% false trust ("Signature Blindness"). Condition 4 (corroborated provenance + epistemic abstention) achieved 100% decision accuracy and 0% false trust at a cost of +1.0 tool call per episode.

## Methods / comparisons
Four matched conditions: (1) no metadata, (2) unsupported textual authority claims, (3) independently verified origin metadata via genuine HMAC-SHA256 detached signatures, and (4) verified origin with independent telemetry corroboration and epistemic abstention. Deterministic 16-case benchmark across a balanced 2×2 epistemic matrix.

## Limitations and unproven claims
Evaluated on deterministic strategy archetypes and synthetic filesystem/telemetry environments; live frontier model variance across diverse prompt wordings requires future multi-model evaluation. Does not address long-term compromised key persistence.

## Next decisive action
Submit sprint research report for Apart Fellowship review; expand benchmark to multi-turn conversational agents and MCP server tools.

See [Literature & Audit](../workstreams/proof-is-not-truth/LITERATURE_AND_AUDIT.md), [Sprint Report](../workstreams/proof-is-not-truth/reports/APART_RESEARCH_REPORT.md), and [Status](../workstreams/proof-is-not-truth/STATUS.md).
