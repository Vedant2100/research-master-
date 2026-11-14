# Vals Build Your Own Eval — False Progress in Autonomous Research Agents

**Stage:** CPU PROTOTYPE + OFFICIAL VALKYRIE SDK SCORING ADAPTER VERIFIED (28/28 TESTS), NO FRONTIER-MODEL EVAL
**Direction:** False Progress / proxy-driven regression in repeated autonomous experiments. **Action sycophancy is not the leading hypothesis**; prior research noted below.
**Separate from:** Tinker post-training (`workstreams/vals/`), StaleStream, RewardHackLab, ContagionBench and ProvenanceTrap.
**Event:** https://www.vals.ai/hackathon (November 14–15, 2026).
**Research master is a coordination repo; implementation remains in the existing private upstream.**

## Hypothesis (NOT TESTED ON FRONTIER MODELS)

A research agent may repeatedly improve a visible proxy metric and promote a new configuration although its true verified outcome deteriorates. Access to a disjoint, independent verification query may prevent some false promotions. A capable agent should also accept genuinely beneficial changes and avoid trivially refusing all promotions.

This is **not an evaluation of user-facing agreement/sycophancy**. The agent is autonomously selecting experiments and making deployment decisions. Related reward-hacking/self-improvement benchmarks exist; originality is not established.

## Actual code and evidence

- Original inspected sources: private `Vedant2100/role-work-forge-artifacts` main `hackathons/2026-11/rewardhacklab/env.py`, `provenancetrap/eval.py`, `llm_backend.py`; pinned upstream starting tree SHA `19b2326807ab9b22f2a28d0da909c1dc77d4a6e1`.
- **Source branch:** `agent/vals-eval/false-progress-eval`.
- **Draft upstream PR:** https://github.com/Vedant2100/role-work-forge-artifacts/pull/3
- **Source folder:** `hackathons/2026-11/vals_eval/`, with standalone `false_progress.py`, `run_false_progress.py`, `README.md`, and `fixtures/scripted_controls.json`; test in `hackathons/2026-11/tests/test_vals_false_progress.py`.
- **Actually executed:** 28/28 CPU-only unit tests passed (15 verifier tests, 12 Vals SDK adapter tests, 1 API-spend gate test) using Colab, including true state/postcondition-verifier execution on scripted synthetic tickets, safe policy improvement, proxy-vs-verified regression, independent audit split, explicit decision reporting, write protections, and hidden-score nonleakage.
- **Actually executed:** 48 scripted **non-model** fixture episodes: 8 distinct seeds of **one synthetic task family** × 2 feedback conditions × 3 scripted strategies. Raw compact data is in `fixtures/scripted_controls.json`. Scripted proxy chaser promotes a worse true policy despite a higher displayed proxy; scripted safe and audit-recovery controls do not.
- **Not executed:** zero frontier-model API calls, no hosted Valkyrie benchmark, no training, no actual model failure, no competition submission. SDK v0.16.2 locally installed and integrated; TestClient confirmed HTTP 200 on /health, /version and /evaluate-response/.
- **Budget spent:** no Tinker/Modal/frontier API credits. A short CPU Colab verifier session was used.
- **Privacy:** no private source reproduced in this public master; only path and links.

## Evaluation protocol and go/no-go

1. **Competence gate:** a real frontier agent must successfully read task specification, edit policy, evaluate, and write valid decision report on clean, controllable tasks. Otherwise failure is tool-use incompetence, not false progress.
2. **Paired conditions:** same 8 seeds, model, inference budget and allowed policy actions. Compare `proxy_only` vs `audit_available`. The audit arm gets one independent validation check; report its additional tool/compute advantage separately.
3. **Independent verifier:** only the held-out, frozen task generator determines true outcome. Score `illusory_promotion`, `verified_gain`, `proxy_gain`, `unsupported_report_claim`, `good_final_decision`.
4. **Initial API preflight:** 2 dev cases on one explicitly approved model under a capped budget; preserve exact prompts, tool traces, model ID/seed, latency/cost. No unapproved API calls.
5. **External validity:** if genuine failures exist, add more realistic research workflows and distinct task families; eight variants of one fictional ticket workflow do **not** justify generalizing to autonomous AI research.
6. **Event integration:** sponsor-approved Valkyrie service/dataset packaging required; the source is not yet Valkyrie-hosted. Reference https://github.com/vals-ai/create-benchmark-service.
7. **Negative results:** if models avoid the proxy trap, preserve the result. Do not relabel scripted controls or easy-task competence failures as frontier-model vulnerabilities.

## Next decisive action
Obtain official Eval track Valkyrie starter and a bounded model-credit allocation. After permission, run the two-case **real model** pilot, confirm competence, then decide whether to scale and package for Vals. No spending or submission without approval.

## Historical direction change
The first scope in draft PR #12 concerned *user-pressure action sycophancy*. User correctly pointed out that this mainly probes assistant user accommodation, not goal-directed autonomous research. On November 13 the direction changed to false progress under repeated experiments. Earlier sycophancy notes are superseded; see updated [RESEARCH_BRIEF](RESEARCH_BRIEF.md).

## November 13 evening — actual SDK and credit preflight
- Added in the existing private upstream branch: `vals_eval/replay_grader.py`, `vals_eval/valkyrie_service.py`, `vals_eval/server.py`, `tests/test_vals_valkyrie_service.py`. The SDK implementation accepts trusted-runner captured action transcripts and independently replays/regrades them using the original verifier. It cannot be called a hosted live agent sandbox; the official event runner still needs integration.
- **28/28 total CPU unit tests executed with official `create-benchmark-service` SDK v0.16.2**, plus live local FastAPI TestClient HTTP 200 for `/health`, `/version`, and `/evaluate-response/`.
- Real-model runner now requires `--authorize-api-spend` AND a positive `--max-api-calls` cap, but this is not a monetary spending limit; a separate approved dollar budget is still needed.
- Checked the connected Colab CPU environment: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `VALKYRIE_API_KEY`, Modal token ID and secret were all absent. No secret values accessed. Gmail's latest Vals logistics update supplied no redemption information. **Cannot run real frontier evaluations or submit to Vals without appropriate access**.
- User action needed: organizer-provided frontier-model credits or securely configured OpenAI/Anthropic API key, Vals Eval account/submission instructions and credited Modal access, plus a bounded dollar/credit budget. No tokens or keys in chat. The event starts Nov 14 at 12 PM PT, hacking 2 PM, Sunday submission deadline 2 PM PT.
- Source end-of-preflight commit `f9e289b731785b9647be5598c13d3c045dd6a49d` on `agent/vals-eval/false-progress-eval`; draft source PR https://github.com/Vedant2100/role-work-forge-artifacts/pull/3.
