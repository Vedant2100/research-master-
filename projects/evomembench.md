# EvoMemBench

**Track:** Memory & Continual Learning  
**Source:** https://github.com/Vedant2100/evo-mem-bench  
**State:** implemented harness and exploratory diagnostic; full matrix unverified  
**Decision:** CONDITIONAL—competence gate first

## Research question
When does prior experience improve a capable frozen agent's later tasks, and which external-memory mechanisms matter?

## Existing evidence
Official CROSSEP-EMB ALFWorld harness with pinned upstream. Full-arm branch includes retrieval, UCB/LinUCB, reflection, consolidation, structured state, evolutionary selection, native adapters. Exploratory hidden-rule diagnostic: no memory 16/36, Reflexion 26/36, UCB 22/36, LinUCB 21/36; heating 0/6. CI green is not model-result evidence.

## Methods / comparisons
No-memory, playbook, random/recent, BM25, success/outcome labels, UCB/LinUCB, Reflexion, ExpeL, Letta-inspired consolidation, A-MEM, ReasoningBank, ACE; distinct LoRA parameter-learning track.

## Limitations and unproven claims
Planned full ~24,090 episode matrix not confirmed complete; synthetic hidden-rule tasks are NOT official ALFWorld; heldout vs sequential online protocols must not be pooled.

## Next decisive action
Run no-memory/playbook headroom (overall >=55%, category >=30%, avoid >95% ceiling), matched seeds, complete held-out core methods before large GPU matrix.

See [evidence ledger](../EVIDENCE.md), [investment assessment](../DECISIONS.md) and [venues](../VENUES.md).