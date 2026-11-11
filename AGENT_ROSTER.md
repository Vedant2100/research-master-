# Agent roster

One named specialist owns one research thread. Public master issues are work queues; the agents are not continuously running by virtue of these files.

| Track | Thread-agent | Scope | Source |
|---|---|---|---|
| Memory & Continual Learning | [`frontiermemory`](.github/agents/frontiermemory.agent.md) | FrontierMemory coding-agent memory audit, paper and replication | [source](https://github.com/Vedant2100/frontiermemory-learning) |
| Memory & Continual Learning | [`evomembench`](.github/agents/evomembench.agent.md) | Official EvoMemBench ALFWorld and separate hidden-rule diagnostic | [source](https://github.com/Vedant2100/evo-mem-bench) |
| Memory & Continual Learning | [`stalestream`](.github/agents/stalestream.agent.md) | CS258 temporal-update memory writer and RL training | [source](https://github.com/Vedant2100/f26/tree/main/cs258/stalestream) |
| Alignment & Agent Safety | [`contagionbench`](.github/agents/contagionbench.agent.md) | Swarm-origin lower-trust peer instruction propagation and independent gate | [source](https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11) |
| Alignment & Agent Safety | [`provenancetrap`](.github/agents/provenancetrap.agent.md) | micro1-origin tool-agent trust-boundary and competence evaluation | [source](https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11) |
| RL Post-Training & Reward Design | [`rewardhacklab`](.github/agents/rewardhacklab.agent.md) | Lexsi-origin task-verified reward and post-training comparisons | [source](https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11) |
| RL Post-Training & Reward Design | [`vals`](.github/agents/vals.agent.md) | Vals event benchmark readiness and actual model optimization | [source](https://www.vals.ai/hackathon) |
| Autonomous Research & Self-Improvement | [`terminal-dreamgym`](.github/agents/terminal-dreamgym.agent.md) | Live-model failure-conditioned practice and transferable skill promotion | [source](https://github.com/Vedant2100/terminal_dreamgym) |
| Autonomous Research & Self-Improvement | [`iterate`](.github/agents/iterate.agent.md) | Iterate participation and DreamGym-based live self-improvement demo | [source](https://luma.com/sht6n8du) |

## Assignment mechanics
Each agent has a dedicated `workstreams/<slug>/STATUS.md`, `.github/agents/<slug>.agent.md` (GitHub Copilot), and `.codex/agents/<slug>.toml` (Codex). Read [operating contract](AGENTS.md). A human/host must invoke the chosen agent and provide access to the original repository if implementation or actual GPU experimentation is requested. Never auto-run nine expensive jobs.
