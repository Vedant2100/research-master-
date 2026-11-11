# ContagionBench / Swarm

**Track:** Alignment & Agent Safety  
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11/contagionbench  
**State:** executed pilot, needs causal replication  
**Decision:** HIGH after independence fix

## Research question
Do lower-trust peer messages induce unauthorized privileged decisions? How much does independent state gating prevent?

## Existing evidence
324 logged Qwen2.5-3B synthetic episodes, 9/96 ungated unsafe choices, 6/96 prompt guard, 0/96 applied unsafe under independent gate; gate blocked nine attempted approvals.

## Methods / comparisons
Randomize independent cases and decode seeds; mediated-vs-direct exposure arms; multi-agent source placement; compare model attempt vs applied state, gate false positives and benign utility.

## Limitations and unproven claims
Greedy seed labels repeated cases (3/32,2/32,0/32), fixed source and direct exposure confound multi-hop contagion claims. Swarm entry was not received by organizer.

## Next decisive action
Complete independent-seed and source/mediator replication; AGENT Nov 20 only if evidence strong; Dec Apart Agent Attribution requires truly new controller-attribution experiments.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).