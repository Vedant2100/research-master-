# Evidence ledger: actual results versus plans

## [FrontierMemory Learning](projects/frontiermemory.md)
**Verified/source-reported:** No memory 6/45; generated memories 7/45, 4/45, 8/45; pooled 19/135 vs 6/45, +0.01/task, p=0.50. Placebo 4/45; read-first 8/45; all-shown 7/45; none-shown 9/45; raw related evidence 9/45. Word2Vec shows content-sensitive gain.
**Interpretation limits:** Only 15 tasks, broken reference solutions for 4; ~8 tasks lacking related source history; no pooled gain ≠ proof memory useless. Generator attempts timed out and exploratory arms must be separately labeled.

## [EvoMemBench](projects/evomembench.md)
**Verified/source-reported:** Official CROSSEP-EMB ALFWorld harness with pinned upstream. Full-arm branch includes retrieval, UCB/LinUCB, reflection, consolidation, structured state, evolutionary selection, native adapters. Exploratory hidden-rule diagnostic: no memory 16/36, Reflexion 26/36, UCB 22/36, LinUCB 21/36; heating 0/6. CI green is not model-result evidence.
**Interpretation limits:** Planned full ~24,090 episode matrix not confirmed complete; synthetic hidden-rule tasks are NOT official ALFWorld; heldout vs sequential online protocols must not be pooled.

## [StaleStream / CS258](projects/stalestream.md)
**Verified/source-reported:** Design written, scoring/headroom checker exists. No verified trained LoRA writer or validated environment.
**Interpretation limits:** Must compute true state from timestamps not delivery order; no hidden-label exposure; memory update ≠ general recursive learning. Reader transfer and injection robustness unproven.

## [ContagionBench / Swarm](projects/contagionbench.md)
**Verified/source-reported:** 324 logged Qwen2.5-3B synthetic episodes, 9/96 ungated unsafe choices, 6/96 prompt guard, 0/96 applied unsafe under independent gate; gate blocked nine attempted approvals.
**Interpretation limits:** Greedy seed labels repeated cases (3/32,2/32,0/32), fixed source and direct exposure confound multi-hop contagion claims. Swarm entry was not received by organizer.

## [ProvenanceTrap / micro1](projects/provenancetrap.md)
**Verified/source-reported:** 96 Qwen2.5-3B episodes, 22/96 correct target, 20/96 strict safe, 0 unauthorized writes and 2 sensitive-read attempts; 60/76 failures quit before writing.
**Interpretation limits:** Weak tool grounding undermines any claimed safety; grader changed after original run; micro1 submission unverified and deadline missed.

## [RewardHackLab / Lexsi](projects/rewardhacklab.md)
**Verified/source-reported:** Tiny Aya Global 4-bit QLoRA trained 16 steps on 84 examples; HF adapter published; 0/6 verified successes baseline and 0/6 after; all 12 evaluations left state untouched.
**Interpretation limits:** SFT NOT GRPO/RL. Decreasing loss is not useful state improvement; no proxy-vs-verified RL experiment yet.

## [Vals AI Benchmaxxing](projects/vals.md)
**Verified/source-reported:** Ticket confirmed Nov 9 for Nov 14–15 at 660 Alabama St, San Francisco; no model/eval/award yet.
**Interpretation limits:** Not a codebase or completed result; must check exact official competition rules and avoid overfitting.

## [Terminal DreamGym](projects/terminal-dreamgym.md)
**Verified/source-reported:** Live Qwen2.5-7B demo baseline train/heldout/adv 2/8,1/6,2/6; reflection 4/8,2/6,1/6; gated 6/8,3/6,4/6. Later two-seed sweep reports zero deltas and 100% false promotion under its metric.
**Interpretation limits:** Single positive demo and null sweep are not same protocol; cannot claim robust self-improvement. Mock runs not evidence of model learning.

## [Iterate AI Research Hack](projects/iterate.md)
**Verified/source-reported:** Event Nov 14–15. DreamGym existing repository is candidate; no evidence of accepted registration, attendance or official submission.
**Interpretation limits:** Overlaps Vals; do not claim both attended or a general recursively self-improving agent.

**Claim labels:** proposed, implemented, executed, replicated, externally submitted, accepted. Do not infer one from another; source repository linked from each project card.