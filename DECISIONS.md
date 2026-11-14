# Investment assessment

All four research tracks stay ACTIVE. We scale code and GPU investment by defensible experimental headroom rather than funding ten workstreams indiscriminately.

- **FrontierMemory Learning: HIGH—finish paper.** Finalize latest generator/blend arm and artifact, freeze figures, decide FORGE Nov 15 submission and save receipt; then per-task oracle-from-history and Word2Vec ablations.
- **EvoMemBench: CONDITIONAL—competence gate first.** Run no-memory/playbook headroom (overall >=55%, category >=30%, avoid >95% ceiling), matched seeds, complete held-out core methods before large GPU matrix.
- **StaleStream / CS258: HIGH—course deliverable.** Nov 12 proposal target; Nov 19 300 held-out episodes with oracle QA >=90% and >=20 point gap vs strongest fair baseline plus measured 20-step timing; Nov 24 GRPO pilot; Dec 3 freeze; Dec 10 report.
- **ContagionBench / Swarm: HIGH after independence fix.** Complete independent-seed and source/mediator replication; AGENT Nov 20 only if evidence strong; Dec Apart Agent Attribution requires truly new controller-attribution experiments.
- **ProvenanceTrap / micro1: CONDITIONAL.** Improve task completion then retest under same scoring; AGENTVERIFY/AGENT or later reliability venue only if evidence matures.
- **RewardHackLab / Lexsi: CONDITIONAL—fix execution first.** Repair tool-call execution to get nonzero baseline, then try real RL; submit honest Lexsi Stage 1 packet by Nov 15 AoE if feasible.
- **Vals AI Benchmaxxing: HIGH time-boxed.** Prepare benchmark and training environment, attend if practical, run baseline→training→eval, preserve code and evidence; avoid spawning an unrelated permanent repo.
- **Terminal DreamGym: DEPRIORITIZED (2026-11-13).** Was "HIGH if replicated"; the gain did not replicate. Four preregistered experiments (handwritten, 7B-written, 30B-written skills; rerun on a new 16-repo benchmark) found no gain from skill text. See [STATUS](workstreams/terminal-dreamgym/STATUS.md).
- **Iterate AI Research Hack: CONDITIONAL time-boxed.** Check approval and event rules; attend only if logistics permit or continue the same research outside the hack.

**Research identity:** RL post-training, continued learning from experience, robust agent evaluation and verifiable autonomous improvement. A negative result can be a useful research contribution with rigorous diagnosis.

## Adaptive Test-Time Compute — conditional investment decision (2026-11-11)

**Worth a low-cost research pilot, not a full training program yet.** TTC aligns especially well with RL/post-training and agentic decision-making; the focus is an experience-conditioned policy for *when* to reason, plan, verify or stop across many tasks. However, adaptive planning via PPO and adaptive reasoning via GRPO already exist. The incremental research opportunity is measurable improvement and retention of compute allocation over a sequence of related tasks, including shifted held-out task families at equal inference budget.

**Go:** existing verified terminal/tool task harness has competence and real compute-sensitive headroom; agent policy improves a cost-quality Pareto point over strong heuristics on heldout shift. **No-go:** no reliable baseline competence, no oracle headroom, or improvements only from unconstrained extra tokens. Priority for initial paper/CS258/Lexsi deadlines remains unchanged. Link: [TTC brief](projects/adaptive-ttc.md), [agent issue #10](https://github.com/Vedant2100/research-master-/issues/10).
