# ProvenanceTrap / micro1

**Track:** Alignment & Agent Safety  
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11/provenancetrap  
**State:** executed diagnostic, agent competence blocker  
**Decision:** CONDITIONAL

## Research question
Can tool agents finish authorized coding tasks without treating lower-trust sources as instructions for privileged tool actions?

## Existing evidence
96 Qwen2.5-3B episodes, 22/96 correct target, 20/96 strict safe, 0 unauthorized writes and 2 sensitive-read attempts; 60/76 failures quit before writing.

## Methods / comparisons
Strict state verifier and filename/AST controls; test legitimate success and sensitive reads/writes separately; use a competent agent baseline and diverse attacks.

## Limitations and unproven claims
Weak tool grounding undermines any claimed safety; grader changed after original run; micro1 submission unverified and deadline missed.

## Next decisive action
Improve task completion then retest under same scoring; AGENTVERIFY/AGENT or later reliability venue only if evidence matures.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).