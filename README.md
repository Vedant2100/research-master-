# Research Portfolio — Five Active Workstreams + One Incubation

This repository is the **research portfolio control plane**: current project status, evidence, decisions and coordination. Canonical experiment code and raw results remain in the source repositories listed in [SOURCE_MAP.md](SOURCE_MAP.md).

**Portfolio snapshot — 2026-11-16:** ten tracked workstreams across four research areas: **five active or conditional**, **one in incubation**, **three completed/deprioritized**, and **one declined**. A configured agent is not an executing agent; every scientific result must be backed by a run and its evidence.

| Area | Workstream | Current state | Agent |
|---|---|---|---|
| Memory & Continual Learning | [FrontierMemory Learning](projects/frontiermemory.md) | **SUBMITTED** — FORGE submission #11; paper cycle complete | `frontiermemory` |
| Memory & Continual Learning | [EvoMemBench](projects/evomembench.md) | **ACTIVE / CONDITIONAL** — partial ALFWorld pilot; lifecycle and competence gates remain | `evomembench` |
| Memory & Continual Learning | [StaleStream / CS258](projects/stalestream.md) | **ACTIVE** — design and preregistration; no trained writer yet | `stalestream` |
| Alignment & Agent Safety | [ContagionBench](projects/contagionbench.md) | **ACTIVE** — pilot complete; causal replication required | `contagionbench` |
| Alignment & Agent Safety | [ProvenanceTrap](projects/provenancetrap.md) | **CONDITIONAL** — competence floor blocks safety conclusions | `provenancetrap` |
| RL Post-Training & Reward Design | [RewardHackLab](projects/rewardhacklab.md) | **ACTIVE / CONDITIONAL** — corrected SFT gate passed; no RL comparison yet | `rewardhacklab` |
| RL Post-Training & Reward Design | [TrustVal](projects/vals.md) | **EXECUTED** — benchmark and model evaluations complete; Vals submission not verified | `vals` |
| RL Post-Training & Reward Design | [Adaptive Test-Time Compute](projects/adaptive-ttc.md) | **INCUBATION** — research design only; no dedicated implementation or runs | `adaptive-ttc` |
| Autonomous Research & Self-Improvement | [Terminal DreamGym](projects/terminal-dreamgym.md) | **DEPRIORITIZED** — preregistered experiments found no reliable gain | `terminal-dreamgym` |
| Autonomous Research & Self-Improvement | [Iterate Research Hack](projects/iterate.md) | **DECLINED** — do not treat as an active opportunity | `iterate` |

## Current operating priorities

1. **StaleStream:** satisfy the timestamp-correct generator, oracle-accuracy, headroom and runtime gates before any substantial RL run.
2. **RewardHackLab:** use the corrected SFT checkpoint for a properly matched proxy-reward versus verified-outcome RL pilot; SFT itself is not an RL result.
3. **EvoMemBench:** verify the 25-reset lifecycle stress test, then clear the no-memory competence gate before resuming the incomplete ALFWorld comparison.
4. **ContagionBench:** establish independent cases/seeds and separate direct from mediated exposure.
5. **ProvenanceTrap:** do not resume safety claims until legitimate task completion is materially improved.
6. **Adaptive TTC:** remain a low-cost incubation project until compute-sensitive headroom and strong cheap baselines are demonstrated.

## How agents work

- The specialist profiles under `.github/agents` and `.codex/agents` are **invocation configurations**, not continuously running workers.
- Use agents only for workstreams still marked active. Completed, declined and deprioritized entries remain for provenance, not as work queues.
- Each agent reads the canonical source repository, runs only within approved access/compute limits, and records exact source SHAs, run IDs, raw evidence, costs, limitations and blockers.
- The coordinator reviews cross-project changes. No agent result is accepted from a plan, code change or green CI alone.

## Tracking and sources

- [Source map](SOURCE_MAP.md): canonical code and evidence locations.
- [Agent roster](AGENT_ROSTER.md) and [coordination protocol](AGENTS.md)
- [Evidence ledger](EVIDENCE.md) · [Investment decisions](DECISIONS.md) · [Roadmap](ROADMAP.md) · [Research venues](VENUES.md) · [Scientific governance](GOVERNANCE.md)
- [Track summaries](tracks) · [Machine-readable index](portfolio.json)
- [Craft research portfolio](https://docs.craft.do/editor/d/dd929934-8174-f727-2930-6f5b7bcce38c/8b4ab40f-4e7e-9c00-0119-df54205b366f)
- [Craft venue tracker](https://docs.craft.do/editor/d/dd929934-8174-f727-2930-6f5b7bcce38c/691adbae-feff-865d-2200-c45600be0fbc)

## Ground rules

Separate **proposed / implemented / executed / replicated / submitted / accepted**. Never infer an external submission or acceptance without a receipt. Negative results remain visible. Keep private code, raw private artifacts, credentials and personal data out of this public repository. The portfolio is a status index; canonical experiment repositories remain the source of truth for code and raw results.
