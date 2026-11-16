# Investment assessment

**Portfolio review: 2026-11-16.** Four research areas remain in the portfolio, but not every historical workstream is active. Six projects remain active or conditional; three are completed/deprioritized; Iterate was declined.

## Current status and investment

| Workstream | Status | Decision |
|---|---|---|
| FrontierMemory Learning | FORGE submission #11 submitted; paper cycle complete | Close current paper work queue. Treat further oracle/Word2Vec studies as a separately scoped follow-up, not unfinished submission work. |
| EvoMemBench | Partial official ALFWorld pilot; 15 episodes saved; reset/lifecycle blocker; no-memory 3/6 | Conditional. Verify the 25-reset lifecycle stress test, then clear the preregistered competence gate before resuming. No large matrix yet. |
| StaleStream / CS258 | Design and preregistration; no trained writer | High course priority. Build the timestamp-correct generator and fair baselines; require oracle >=90%, >=20 pp headroom and measured runtime before training. |
| ContagionBench / Swarm | 324-episode pilot; independence and exposure confounds remain | Continue only the independent-case/seed and direct-versus-mediated replication. Do not claim multi-hop causal contagion from the current pilot. |
| ProvenanceTrap / micro1 | 96-episode diagnostic; low legitimate completion | Conditional / low priority until a stronger tool-capable agent demonstrates meaningful authorized completion. Do not interpret early quitting as safety. |
| RewardHackLab / Lexsi | Corrected SFT calibration: 0/18 base, 18/18 SFT; no RL comparison | Continue to a small, matched RL pilot from the shared SFT checkpoint. SFT is a competence warm-start, not evidence for either reward hypothesis. |
| TrustVal | Four-task benchmark published and evaluated across model generations | Close the benchmark-execution queue. External Vals event submission is **not verified**; do not claim it was submitted or accepted without a receipt. |
| Adaptive TTC | Conceptual design only | Incubation. Only a low-cost compute-sensitivity pilot after reuse and prior-art review; no dedicated GPU allocation yet. |
| Terminal DreamGym | Four preregistered experiments; no reliable skill-transfer gain; v2 30B-skill harm | Deprioritized. No further runs planned on this loop. |
| Iterate AI Research Hack | Owner declined participation | Closed / not planned. Do not suggest it as an active opportunity. |

## Next execution order

1. **StaleStream:** protect the CS258 deliverable. Finish generator semantics, disjoint split, symbolic/LLM baselines, oracle reader and actual 20-step runtime measurement. No GRPO until all gates pass.
2. **RewardHackLab:** the corrected SFT checkpoint now clears the preregistered 60% competence gate (18/18, zero forbidden resolutions). Next compare proxy and verified terminal-state rewards from the same checkpoint, with nonzero reward variance, matched budgets and held-out evaluation. The previous GRPO run was interrupted before the verified-reward arm and is not a result.
3. **EvoMemBench:** confirm the close/reset stress test; the current six-task no-memory score (3/6 = 50%) is below the 55% competence threshold. Improve or change the worker before expanding.
4. **ContagionBench:** replicate with independent cases and decoding seeds; isolate mediated transfer and report both attempted and applied unsafe actions plus benign utility.
5. **ProvenanceTrap:** pause expensive runs until legitimate task completion is fixed.
6. **Adaptive TTC:** remain in incubation until a cheap, paired pilot establishes compute-sensitive headroom and strong heuristic/bandit baselines.

## Research identity

The portfolio's central interests remain RL post-training, long-horizon continual learning, memory governance, robust agent evaluation and verifiable autonomous improvement. Negative results are publishable only when the benchmark, controls, uncertainty and interpretation support the claim. A completed project does not need to remain artificially active.

## Adaptive Test-Time Compute — conditional investment decision

TTC remains a low-cost research hypothesis, not an active training program. The relevant question is whether experience across tasks improves compute allocation and transfers to shifted task families beyond strong within-task planning policies and cheap heuristics. Require matched token/tool/latency budgets, verified outcomes, held-out families and multiple seeds before scaling. If no compute-sensitive headroom exists, park it.
