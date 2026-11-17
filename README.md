# Research Master — Four Active Tracks, Ten Specialist Agents

This portfolio coordinates **ten workstreams across four research areas**, not ten simultaneously running experiments. One named specialist owns each thread. Status and completed phases are reconciled against their canonical source repositories.

**2026-11-16 status:** FrontierMemory paper/study completed (FORGE submission #11 user-reported, receipt not stored here); TrustVal v3/v4 evaluations completed (Vals event submission unverified); Terminal DreamGym four-experiment cycle completed/deprioritized. RewardHackLab corrected SFT competence gate passed but its actual proxy-vs-verified RL comparison is outstanding. StaleStream, EvoMemBench, ContagionBench and ProvenanceTrap retain experiment gates; Adaptive TTC is conceptual. Iterate event not pursued.

| Area | Thread | Agent |
|---|---|---|
| Memory & Continual Learning | [FrontierMemory Learning](projects/frontiermemory.md) | `frontiermemory` |
| Memory & Continual Learning | [EvoMemBench](projects/evomembench.md) | `evomembench` |
| Memory & Continual Learning | [StaleStream / CS258](projects/stalestream.md) | `stalestream` |
| Alignment & Agent Safety | [ContagionBench](projects/contagionbench.md) | `contagionbench` |
| Alignment & Agent Safety | [ProvenanceTrap](projects/provenancetrap.md) | `provenancetrap` |
| RL Post-Training & Reward Design | [RewardHackLab](projects/rewardhacklab.md) | `rewardhacklab` |
| RL Post-Training & Reward Design | [TrustVal (Vals Build Your Own Eval)](projects/vals.md) | `vals` |
| RL Post-Training & Reward Design | [Adaptive Test-Time Compute (TTC)](projects/adaptive-ttc.md) | `adaptive-ttc` |
| Autonomous Research & Self-Improvement | [Terminal DreamGym](projects/terminal-dreamgym.md) | `terminal-dreamgym` |
| Autonomous Research & Self-Improvement | [Iterate Research Hack](projects/iterate.md) | `iterate` |

## How agents work

- **GitHub Copilot**: select a [custom agent profile](.github/agents) in a supported client; point it at the corresponding project and [work issue](AGENT_ROSTER.md). GitHub profiles require supported Copilot access.
- **Codex**: use the [project-scoped agent configurations](.codex/agents), with [root agent coordination rules](AGENTS.md). Start a Codex multi-agent session and delegate explicitly; configuration does not run agents on its own.
- **Each agent works in a separate research lane**: read the evidence; implement/run only with authorized repo+compute access; open a PR for review; record experiments in [the handoff template](templates/EXPERIMENT_HANDOFF.md). No self-certifying a result.
- **Orchestrator/human** reviews cross-project changes and decisions. Agent branches are never implicitly merged.

## Tracking and sources

- **[Source map](SOURCE_MAP.md): where each workstream's prior code lives, to import into `workstreams/<slug>/` and build on rather than reinvent.**


- [Ten-agent roster](AGENT_ROSTER.md) and [coordination protocol](AGENTS.md)
- [Evidence ledger](EVIDENCE.md) · [Investment decisions](DECISIONS.md) · [Roadmap](ROADMAP.md) · [Research venues](VENUES.md) · [Scientific governance](GOVERNANCE.md)
- [Track summaries](tracks) · [Machine-readable index](portfolio.json)
- [Craft research portfolio](https://docs.craft.do/editor/d/dd929934-8174-f727-2930-6f5b7bcce38c/8b4ab40f-4e7e-9c00-0119-df54205b366f)
- [Craft venue tracker](https://docs.craft.do/editor/d/dd929934-8174-f727-2930-6f5b7bcce38c/691adbae-feff-865d-2200-c45600be0fbc)

## Ground rules

All four research areas remain in scope, but closed projects do not need recurring execution; prioritize unfinished work by evidence and deadlines. Separate **planned / implemented / executed / replicated / submitted / accepted**. CI success is not experiment evidence. Do not infer a user has registered/submitted without receipt. The central repo is **public**: no private notes, personal data, secrets, cluster credentials, or inaccessible private experiment code should be copied here.

**Important:** Creating these agent profiles and issues makes them *available for invocation*, not continuously running or independently funded. Execution requires a supported agent runtime and access to the original experiment repos/GPUs.
