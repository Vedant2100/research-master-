# Proof Is Not Truth (AI × Epistemics)

**Track:** Trust Infrastructure / Model Epistemics (Apart AI × Epistemics Sprint, November 13–15, 2026)  
**Source:** `workstreams/proof-is-not-truth/`  
**State:** EXPLORATORY LOCAL QWEN2.5-7B QUICK PILOT (25 EPISODES; ONE MODEL/SEED); FULL SUITE NOT RUN  
**Decision:** ACTIVE, BUT EMPIRICAL CLAIMS REQUIRE REVISION

## Research question

When tool-using agents consume machine-verifiable provenance, do they distinguish origin authenticity from factual correctness when taking consequential actions, and can independent factual corroboration improve decisions without causing blanket abstention?

## Current evidence

- The 16-case benchmark and five evaluation conditions are implemented.
- A live local Qwen2.5-7B quick pilot ran 25 episodes: five representative cases × five conditions, one greedy seed. It is not a full 16-case or multi-seed evaluation.
- On one authentic-false CI case, the model verified a valid HMAC-SHA256 MAC and deployed a false release tag. The same false action occurred under no-metadata, textual-authority, and telemetry-only conditions; this does not establish that provenance caused the failure.
- The telemetry arms queried a nonexistent `deployment_status` metric and did not follow up on the available `ci_test_runner` metric. The combined arm abstained on every pilot case (100% abstention; 0% legitimate task completion), so it has not demonstrated calibrated corroboration.
- HMAC-SHA256 is a keyed message authentication code, not an asymmetric digital signature.

## Required next evidence

1. Repair the grader's exact-string clean-task check and abstention metrics.
2. Add metric discovery and ensure telemetry can be queried successfully.
3. Run the complete 16-case matrix, with multiple task instances/runs.
4. Demonstrate fewer false actions while retaining legitimate task completion; blanket abstention is not a successful defense.
5. Revise the report's causal and generalization claims and accurately position Learn2Discern, What Counts as Evidence, Auditing Provenance Sensitivity, and ProvenanceGuard.

See [Next Steps and Validity Audit](../workstreams/proof-is-not-truth/NEXT_STEPS_2026-11-14.md), [Status](../workstreams/proof-is-not-truth/STATUS.md), and [Literature & Audit](../workstreams/proof-is-not-truth/LITERATURE_AND_AUDIT.md).
