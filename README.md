# Research Master — Four Active Tracks, Nine Specialist Agents

The research portfolio coordinating **nine distinct workstreams across four continuously active areas**. **One agent owns one thread.** This repository is the *coordination hub*, not a duplicate of the experiments' source repositories.

| Area | Thread | Agent |
|---|---|---|
| Memory & Continual Learning | [FrontierMemory Learning](projects/frontiermemory.md) | `frontiermemory` |
| Memory & Continual Learning | [EvoMemBench](projects/evomembench.md) | `evomembench` |
| Memory & Continual Learning | [StaleStream / CS258](projects/stalestream.md) | `stalestream` |
| Alignment & Agent Safety | [ContagionBench](projects/contagionbench.md) | `contagionbench` |
| Alignment & Agent Safety | [ProvenanceTrap](projects/provenancetrap.md) | `provenancetrap` |
| RL Post-Training & Reward Design | [RewardHackLab](projects/rewardhacklab.md) | `rewardhacklab` |
| RL Post-Training & Reward Design | [Vals Benchmaxxing](projects/vals.md) | `vals` |
| Autonomous Research & Self-Improvement | [Terminal DreamGym](projects/terminal-dreamgym.md) | `terminal-dreamgym` |
| Autonomous Research & Self-Improvement | [Iterate Research Hack](projects/iterate.md) | `iterate` |

## How agents work

- **GitHub Copilot**: select one of the nine [custom agent profiles](.github/agents) in a supported client; point it at the corresponding project and [work issue](AGENT_ROSTER.md). GitHub profiles require supported Copilot access.
- **Codex**: use the nine [project-scoped agent configurations](.codex/agents), with [root agent coordination rules](AGENTS.md). Start a Codex multi-agent session and delegate explicitly; configuration does not run agents on its own.
- **Each agent works in a separate research lane**: read the evidence; implement/run only with authorized repo+compute access; open a PR for review; record experiments in [the handoff template](templates/EXPERIMENT_HANDOFF.md). No self-certifying a result.
- **Orchestrator/human** reviews cross-project changes and decisions. Agent branches are never implicitly merged.

## Tracking and sources

- **[Canonical upstream code map — required for all nine agents](SOURCE_MAP.md): reuse source repositories and existing results; do not reinvent or copy them.**


- [Nine-agent roster](AGENT_ROSTER.md) and [coordination protocol](AGENTS.md)
- [Evidence ledger](EVIDENCE.md) · [Investment decisions](DECISIONS.md) · [Roadmap](ROADMAP.md) · [Research venues](VENUES.md) · [Scientific governance](GOVERNANCE.md)
- [Track summaries](tracks) · [Machine-readable index](portfolio.json)
- [Craft research portfolio](https://docs.craft.do/editor/d/dd929934-8174-f727-2930-6f5b7bcce38c/8b4ab40f-4e7e-9c00-0119-df54205b366f)
- [Craft venue tracker](https://docs.craft.do/editor/d/dd929934-8174-f727-2930-6f5b7bcce38c/691adbae-feff-865d-2200-c45600be0fbc)

## Ground rules

Four tracks stay active each week; effort varies by validated promise and deadlines. Separate **planned / implemented / executed / replicated / submitted / accepted**. CI success is not experiment evidence. Do not infer a user has registered/submitted without receipt. The central repo is **public**: no private notes, personal data, secrets, cluster credentials, or inaccessible private experiment code should be copied here.

**Important:** Creating these agent profiles and issues makes them *available for invocation*, not continuously running or independently funded. Execution requires a supported agent runtime and access to the original experiment repos/GPUs.
