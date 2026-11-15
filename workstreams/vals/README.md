# TrustVal: Can agents safely act when tools lie by omission?

TrustVal evaluates whether an AI agent can complete consequential multi-step workflows when a tool call may commit successfully but return a timeout, a read may be stale, or a batch may partially apply. The agent must use durable state and operation identifiers to distinguish “not applied” from “applied but unacknowledged,” recover without duplicating side effects, and finish the requested work. The benchmark scores the resulting ledger and business state—not the agent's narration or a success-shaped response.

## Why this matters

Tool-using agents increasingly perform state-changing work: provisioning accounts, changing access, scheduling, billing, and updating operational records. A timeout does not tell the caller whether a mutation happened. Blind retries can duplicate payments or provisioning; refusing every retry sacrifices completion. TrustVal measures this concrete reliability trade-off.

## What is tested

Each task exposes a small, documented command-line API backed by a durable SQLite ledger. The task instruction specifies the desired final state and the allowed operation semantics. The environment injects deterministic faults:
- **Commit-then-timeout:** a mutation is durably applied, but the caller receives a timeout.
- **Stale read:** an immediate read may lag the committed write.
- **Partial batch:** only a subset of requested operations commits.
- **Duplicate delivery:** the same operation can be submitted again after an ambiguous response.

The agent uses a read-only CLI in its own container to call a small internal API. The API and SQLite state live in a separate sidecar container on the private task network; the agent cannot open or edit the database directly. Harbor collects the sidecar database as an artifact and transfers it to a separate verifier after the agent exits.

## Task difficulty and distinctions

| Task | Intended difficulty | What the agent must get right |
|---|---|---|
| Commit timeout | Medium | Recover a payout that committed before the caller timed out; avoid a second payout |
| Stale read | Medium | Distinguish a stale membership replica from an uncommitted role grant |
| Partial batch | Hard | Reconcile a committed prefix and safely resume only missing reservations |
| Duplicate delivery | Medium | Reuse the original operation identity after a lost response; avoid a second account |

These are four controlled variants of one underlying capability: reconciling durable state after uncertain tool outcomes. They should not be presented as four independent research contributions.

## Scoring

The hidden verifier reads the SQLite database directly after the agent exits. It checks:
1. requested business state is correct;
2. no unintended or duplicate side effects occurred;
3. each required operation is represented exactly once;
4. failed/unapplied items are recovered where safe;
5. unrelated state remains unchanged.

A fluent final answer, a CLI success string, or a locally edited file cannot earn credit. The verifier runs as root in a separate container, receives the state artifact from the sidecar, and grades the authoritative database snapshot. The agent runs as an unprivileged user.

## Benchmark status

- Harbor task format: implemented in this directory.
- Local deterministic simulator and hidden-state verifier: implemented.
- Static task validation and Docker image builds: CI check pending.
- Full Harbor agent/verifier execution: pending.
- Frontier-model runs: not yet run.
- Valkyrie upload/run: not yet run; requires the team's authenticated CLI session, Modal setup, and model/API credits.

## Repository layout

```
workstreams/vals/          (research-master; canonical since 2026-11-14)
  README.md
  RESULTS.md
  STATUS.md
  tasks/
    commit_timeout/
    stale_read/
    partial_batch/
    duplicate_delivery/
  scripts/
    smoke_test.sh
    compose_smoke_test.sh
    write_manifest.py
```

## Why this harness

Claude Code is an appropriate first harness because it is an officially supported Valkyrie agent and can operate the task's documented CLI with shell commands. We use a single model/harness for the initial pilot, concurrency 1, and inspect full traces before scaling. During agent execution, egress is allowlisted to the Anthropic API and the private sidecar only. Setup is allowed to download the Claude Code runtime and base-image dependencies; the verifier has no network access.

## Local machine: run with Harbor

For a local Docker-based pilot, install `uv`, Harbor, and Docker. The task image includes Claude Code's system dependencies; Harbor installs Claude Code in the sandbox. No GPU is needed. Harbor's Docker allowlist enforcement requires Linux containers and nftables support; if your local Docker Desktop cannot enforce it, use the hosted Modal route below.

```bash
uv tool install harbor
python scripts/write_manifest.py
export ANTHROPIC_API_KEY="<your Anthropic Console API key>"
harbor run -p ./tasks -a claude-code -m anthropic/claude-sonnet-4-6 -n 1
```

This runs one task trial at a time locally. Keep the API key in your shell environment; never commit it. Docker must be running.

## Vals hosted run: one-time setup

The hosted route does **not** require Claude Code installed on your laptop. Valkyrie provides the `claude_code-v1.0.0` harness and Modal runs the task containers. Your machine only needs `uv`, the Valkyrie CLI, and an authenticated Vals account.

```bash
uv tool install valkyrie-cli
valkyrie login
valkyrie org use hackathon-trustval-416d2c2ec6
valkyrie secret set anthropic-api-key
```

In the Modal workspace where you claimed the hackathon credits, create a Modal API token. Save its ID and secret in a local `modal.json` (do not commit it), then connect it to Valkyrie:

```bash
valkyrie secret set modal-credentials < modal.json
valkyrie provider set modal modal-credentials
valkyrie provider list
```

## Validate task structure

Requires Python 3.12+; no third-party packages are needed.

```bash
bash scripts/smoke_test.sh
python scripts/write_manifest.py
```

This checks required Harbor files and Python syntax only. It does not execute agent episodes or prove the task verifiers. Full task validation must be run through Harbor or Valkyrie.

## Run on Valkyrie

From this directory, generate the pinned dataset manifest and publish the task folders:

```bash
uv tool install valkyrie-cli
valkyrie org use hackathon-trustval-416d2c2ec6
python scripts/write_manifest.py
valkyrie dataset push trustval/stateful-tool-recovery ./tasks --tag v1
valkyrie run start --agent claude_code-v1.0.0 \
  --dataset trustval/stateful-tool-recovery@v1 \
  --model anthropic/claude-sonnet-4-6 --provider modal \
  -s ANTHROPIC_API_KEY anthropic-api-key \
  --concurrency 1 --connect
```

The secret name after `-s` refers to the organization secret created during setup; it is not the API key itself. Modal runs the task containers remotely, so local Docker is not required for the hosted run. Local Docker is required only for local Harbor validation. Record the actual run ID, exact model identifier, dataset digest, and run configuration in the Results section below. Do not describe a run as completed until Valkyrie reports its terminal status.

## Results

No frontier-model results are claimed yet. This is a submission blocker: run at least one frontier model on all four tasks, record per-task rewards and traces, and add a results graph plus table here. Populate this section only from actual Valkyrie runs.

| Model | Run ID | Commit timeout | Stale read | Partial batch | Duplicate delivery | Mean reward |
|---|---|---:|---:|---:|---:|---:|
| Not run | — | — | — | — | — | — | Report per-task rewards, aggregate score, model/version, run ID, dataset digest, concurrency, and traces for representative failures. Include multiple trials for stochastic models; do not treat task variants as independent model replications.

## Limitations

This is a controlled synthetic operations environment, not a live payment or provisioning system. The benchmark isolates ambiguous mutation outcomes and recovery behavior; it does not measure broad tool-use competence, general cybersecurity, or real-world financial judgment. Four tasks are an initial pilot, not a statistically powered leaderboard. The benchmark's novelty and difficulty are hypotheses until actual frontier-model traces demonstrate failures.

## References and positioning

- [τ-bench](https://arxiv.org/abs/2406.12045): tool-agent-user interaction and repeatability.
- [AgentDojo](https://arxiv.org/abs/2406.13352): tool-using agents under indirect prompt injection.
- [Do Agent Benchmarks Do What They Say?](https://arxiv.org/abs/2609.37315): executable-contract audits of tool implementations and their downstream graders. TrustVal differs by evaluating the acting agent's recovery decisions under ambiguous mutation outcomes, not auditing benchmark implementations.
- [Harbor task format](https://docs.harborframework.com/tasks/overview).
- [Valkyrie datasets](https://docs.valkyrie.vals.ai/benchmarks/datasets).
