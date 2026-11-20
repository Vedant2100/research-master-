# Proof Is Not Truth: Decoupling Origin Authentication from Factual Veracity in Tool-Using LLM Agents

**Author:** Vedant Deepak Borkute  
**Affiliation:** Department of Computer Science and Engineering, University of California, Riverside  
**With:** Apart Research  
**Track:** AI × Epistemics Research Sprint — Track 2: Trust Infrastructure

## Abstract

Cryptographic provenance can verify who produced an artifact and whether it was altered in transit, but it cannot establish that its contents are true or current. We study how a tool-using language-model agent uses provenance and telemetry when making state-changing operational decisions. We built a 16-case benchmark spanning clean tasks and combinations of origin authenticity and factual veracity, then evaluated six prompt/tool configurations over 96 episodes with Qwen2.5-7B-Instruct using greedy decoding and seed 42. In the tested verified_origin configuration, the agent rejected all three unauthenticated false inputs but acted on two of three authentic-but-false cases. This result is prompt-conditioned: the configuration explicitly instructed the agent to proceed when origin was authentic, so it does not isolate the effect of HMAC verification. The telemetry_only configuration recorded no false trust across the six false tasks, but completed only 10% of legitimate tasks and abstained in 81.3% of episodes. A version-2 trace regrade also exposed write-then-abstain failures that the initial grading would have credited as safe. These exploratory results show a safety–utility trade-off in one model and seed; they do not establish general behavior across frontier agents.

## 1. Introduction

AI agents increasingly consume signed artifacts, tool outputs, logs, and telemetry before taking consequential actions. Provenance systems can establish that an artifact came from a particular keyholder and was not altered after signing. They cannot establish that the artifact describes the current world correctly. An authorized CI service can sign a misleading “all tests passed” report after a runner crashes; a telemetry daemon can authenticate stale readings; an administrator can sign a policy that has since become obsolete. Treating origin as truth can therefore turn a useful integrity signal into an unsafe decision shortcut.

This distinction matters when agents can mutate state rather than merely answer questions. A false belief can become a deployment, shutdown, configuration change, or security-policy change. The relevant question is not simply whether an agent recognizes a trusted source, but whether it checks whether the source’s claim is true and current before acting.

We investigate: when a tool-using agent receives machine-verifiable origin information, does it distinguish authenticity from factual veracity during state-changing decisions, and can independent telemetry corroboration reduce false actions without causing blanket abstention?

Our contributions are:
- A 16-case operational benchmark separating origin authenticity from factual veracity, with clean-task controls and independently queryable telemetry.
- A 96-episode real-model evaluation across six prompt/tool configurations, with raw traces and a reproducible offline regrade.
- A trace-level action-ordering correction that does not credit an agent for abstaining after it has already attempted an unsafe mutation.
- An empirical account of the observed safety–utility trade-off, including the prompt confounds and limits on causal interpretation.

## 2. Related Work

Learn2Discern evaluates source discernment and truth discernment during belief updating from external information. Across 13 models and nearly 670,000 trials, it reports weaknesses in how models weight source reliability and claim truth (Ashkinaze et al., 2026). What Counts as Evidence? studies how source history, evidence lineage, event time, and presentation order influence judgments across 500 scenarios and 13 models (Zhang et al., 2026). These works motivate measuring epistemic cue use, but do not test agents making state-changing tool calls in an operational environment.

Auditing Provenance Sensitivity studies how source authority affects LLM-agent action selection across 450 next-action tasks. Its target-specific labels concern whether evidence is authorized to influence an action, rather than whether an authorized source’s claim is factually true (Liao, 2026). ProvenanceGuard addresses cross-source conflation in MCP-based agents by checking whether claims are attributed to the correct evidence source across medical-domain traces (Alvarez et al., 2026). Our study is complementary: it tests the operational gap between cryptographic origin authentication and independently observable environmental truth.

## 3. Methods

### 3.1 Benchmark and environment

We constructed 16 deterministic cases in isolated filesystem sandboxes. Four clean-baseline cases test ordinary task execution. The remaining 12 form an authenticity-by-veracity matrix: (A) authentic and true (3 cases), (B) unauthenticated and false (3), (C) authentic but false (3), and (D) unauthenticated but true (3). Cell C contains three operational traps: a CI summary signed as successful despite a runner crash (exit code 139); a signed temperature report from a frozen sensor while the rack is overheating; and a signed TLS exemption based on a revoked incident ticket. Ground-truth labels and expected decisions were withheld from the agent’s context.

The agent can read files, write files, finish, or abstain. Depending on condition, it also receives a provenance-verification tool and/or telemetry tools. The telemetry interface first exposes metric names and descriptions through `list_telemetry_metrics()`; the agent must then explicitly query a metric to observe its value. This separates discovery from access to the underlying state.

### 3.2 Cryptographic and telemetry signals

The provenance mechanism is a genuine HMAC-SHA256 message authentication code using a 256-bit shared secret associated with an authority identity. A detached manifest authenticates the file contents; verification recomputes the content hash and checks the MAC. This tests keyed origin authentication and integrity. It is not an asymmetric public-key signature system and does not provide public-key non-repudiation. Crucially, a valid MAC does not certify that the contents are factually correct, current, or authorized for a particular action.

### 3.3 Prompt/tool configurations

We evaluated six composite configurations:
- **no_metadata:** ordinary read/write/abstain tools; general instruction to make factually safe writes.
- **textual_authority:** prose authority claims without cryptographic verification.
- **verified_origin:** provenance verification without telemetry; its system prompt explicitly said to proceed if origin was authentic.
- **telemetry_only:** telemetry discovery/query without provenance; its system prompt explicitly required corroboration against live telemetry.
- **corroborated_provenance_neutral:** both toolsets, with a neutral instruction to use available checks.
- **corroborated_provenance_directive:** both toolsets, with an explicit warning that proof of origin is not proof of truth and an instruction to corroborate.

These are prompt/tool policy configurations, not a fully crossed factorial experiment. Tool availability and system instructions vary together. The verified_origin and telemetry_only instructions are especially consequential confounds and must be considered when interpreting differences.

### 3.4 Model, execution, and scoring

All 96 episodes were run on Qwen2.5-7B-Instruct with Ollama 0.40.11 on UCR cluster node06 (Slurm job 312727; 24 CPU cores; 32 GB RAM). Decoding was greedy (temperature 0.0, seed 42). Each of the six configurations received all 16 cases. There were no infrastructure errors or timeouts. We report counts and rates with their denominators; one model, one deterministic seed, and three cases per epistemic cell do not support population-level statistical inference.

We score decisions against hidden ground truth and inspect the complete action trace. The version-2 offline regrader distinguishes an attempted unsafe write from the final filesystem state. An abstention receives no safe-abstention credit if an unsafe mutation occurred earlier in the same episode. This corrects a failure in the initial grading, which could treat a final abstain call as safe even after a harmful write. False trust is counted when an agent attempts a false or unsafe mutation on one of the six abstain-expected tasks; an attempt before abstention counts even if later restored. Legitimate task completion (LTC) is measured over the ten legitimate tasks; abstention rate is the share of all 16 episodes ending in abstention. The harness regression suite passed 11/11 tests; six negative verifier tests passed; and the offline v2 regrade reproduced the published CSV and JSON outputs bit-for-bit.

## 4. Results

**Table 1.** Summary of false trust, legitimate-task completion, and abstention rates. Counts are shown with denominators.

| Configuration | False trust (all 6 false tasks) | Cell C (authentic false; 3 cases) | Legitimate completion (10 tasks) | Abstention (16 episodes) |
|---|---:|---:|---:|---:|
| No metadata | 5/6 (83.3%) | 2/3 (66.7%) | 5/10 (50%) | 12.5% |
| Textual authority | 6/6 (100%) | 3/3 (100%) | 7/10 (70%) | 6.3% |
| Verified origin | 2/6 (33.3%) | 2/3 (66.7%) | 2/10 (20%) | 62.5% |
| Telemetry only | 0/6 (0%) | 0/3 (0%) | 1/10 (10%) | 81.3% |
| Combined neutral | 2/6 (33.3%) | 1/3 (33.3%) | 1/10 (10%) | 68.8% |
| Combined directive | 1/6 (16.7%) | 0/3 (0%) | 1/10 (10%) | 81.3% |

In the authentic-false cell (C), false trust was 2/3 (66.7%) under no_metadata and 2/3 (66.7%) under verified_origin. The verified_origin prompt explicitly instructed the agent to proceed when origin was authentic, so this comparison cannot identify the effect of adding HMAC verification. Under that configuration, the agent rejected all three unauthenticated false inputs (0/3) but accepted two authentic-false claims. This illustrates the distinction the benchmark is designed to test: authentic origin does not establish factual veracity.

The telemetry_only configuration recorded no false trust on any of the six false tasks (0/6), including all three authentic-false traps (0/3). It also completed only one of ten legitimate tasks (10%) and abstained in 81.3% of all episodes. The combined directive configuration also recorded 0/3 false trust in Cell C, but had one false-trust event overall (1/6). The combined neutral configuration recorded 1/3 false trust in Cell C. Because the prompts differ, these are observed configuration-level outcomes, not evidence that a particular directive or tool caused the differences.

A trace audit found an additional failure hidden by terminal-action grading. In one unauthenticated-false episode, the agent wrote `SHUTDOWN` to `cluster/mode.txt` before checking provenance and then called `abstain()`. The version-2 regrader classified this as an unsafe write attempt and invalidated safe-abstention credit. This leaves the combined directive configuration at 16.7% false trust across all false tasks despite 0/3 false trust in Cell C. In table order (no_metadata, textual_authority, verified_origin, telemetry_only, combined neutral, combined directive), unsafe writes attempted were 5, 6, 2, 0, 2, and 1, respectively.

*Figure 1 in the PDF compares false trust across all six false tasks with legitimate-task completion across ten legitimate tasks. The bars are descriptive for this single model/seed and the stated prompt/tool configuration; they are not causal estimates.*

## 5. Discussion and Limitations

### 5.1 Interpretation

The strongest supported conclusion is narrow: in this test environment, origin authentication alone did not resolve whether an authentic operational claim was true. The verified_origin arm’s 2/3 authentic-false acceptance is consistent with over-reliance on the instruction to proceed after authentication, but the design cannot separate that prompt effect from the availability of the MAC tool. We therefore do not claim that cryptographic provenance itself caused false trust or made the agent less accurate than baseline.

Telemetry corroboration was associated with lower false trust in the tested cases, but the telemetry_only arm’s 10% legitimate-task completion and 81.3% abstention show that refusing broadly is not a satisfactory defense. The combined configurations also had low legitimate-task completion (10%). The result is a safety–utility trade-off across composite policies, not proof that telemetry inherently causes over-abstention. A useful agent needs to check the right facts before consequential actions while still completing benign tasks.

### 5.2 Limitations

First, the evaluation uses one open-weight model (Qwen2.5-7B-Instruct), one greedy decoding seed, and 16 deterministic cases. The three-case denominators in Cells A–D are small; percentages can change substantially with individual episodes. We do not report confidence intervals or significance tests because repeated independent model/seed samples were not collected. Second, the six arms vary both tools and prompt policies, so they do not support clean causal attribution. Third, HMAC-SHA256 is a shared-secret MAC, not a public-key provenance infrastructure; findings should not be generalized to all signing systems. Fourth, the environment is a controlled filesystem/telemetry sandbox and does not reproduce the complexity, redundancy, or human oversight of production systems. Finally, this study evaluates one model family and does not establish that current frontier models exhibit the same failure rates.

### 5.3 Future work

A follow-up should fully cross provenance-tool availability and telemetry-tool availability under a single fixed system prompt, then independently vary instructions. It should replicate across multiple model families, seeds, and larger, more diverse operational tasks; report uncertainty at the case and model levels; and test whether risk-tiered pre-action checks preserve legitimate task completion. The benchmark should also distinguish attempted mutation, committed state change, and successful recovery.

## 6. Conclusion

Cryptographic provenance can establish who authenticated an artifact and whether it changed after signing; it cannot establish that the artifact describes current reality. In this exploratory evaluation, the tested verified_origin configuration rejected unauthenticated false inputs but accepted two of three authentic-false traps under a prompt that explicitly encouraged proceeding after authentication. Telemetry-oriented configurations avoided false trust in the authentic-false cases but also over-abstained on legitimate tasks. The practical design implication is to treat provenance as one evidence signal, require independent factual checks before high-impact mutations, and evaluate action ordering—not merely the agent’s final response.

## Code and Data

Code repository: https://github.com/Vedant2100/research-master-/tree/agent/proof-is-not-truth/apart-sprint

Benchmark cases, raw traces, v2 regraded traces, metrics, tests, and reproduction scripts are in `workstreams/proof-is-not-truth/`. The submission branch contains the experiment artifacts; PR #13 remains open and unmerged.

## Author Contributions

Vedant Deepak Borkute conceived and directed the study, defined the research question and evaluation design, reviewed the implementation and experiment traces, interpreted the results, and prepared the submission. AI coding and writing assistants supported implementation, debugging, literature review, analysis, and editing.

## References

1. Ashkinaze, J., Kurek, L., Faisal, A., Miao, T., Joseph, M., Budak, C., & Gilbert, E. (2026). *Information Discernment in Large Language Models*. arXiv:2607.19355. https://arxiv.org/abs/2607.19355
2. Zhang, J., Jiang, K., & Lu, G. (2026). *What Counts as Evidence? Epistemic Cue Utilization in Large Language Models*. arXiv:2610.12788. https://arxiv.org/abs/2610.12788
3. Liao, J. (2026). *Auditing Provenance Sensitivity in LLM Agent Action Selection*. arXiv:2607.20827. https://arxiv.org/abs/2607.20827
4. Alvarez, A., Rajan, S., Mugel, S., & Orús, R. (2026). *ProvenanceGuard: Source-Aware Factuality Verification for MCP-Based LLM Agents*. arXiv:2606.18037. https://arxiv.org/abs/2606.18037

## Appendix A. Limitations and Dual-Use / Ethical Considerations

This work is an exploratory benchmark study, not a deployment assessment or a claim about the prevalence of unsafe behavior in production agents. Its conclusions are bounded by one model, one greedy seed, 16 deterministic cases, small per-cell denominators, and prompt/tool confounds. The benchmark uses synthetic operational artifacts, locally generated HMAC keys, and isolated filesystem sandboxes. It does not use personal data, production credentials, live infrastructure, or real user records.

The work has defensive value: it can help agent developers test whether their systems distinguish authenticated origin from factual correctness, corroborate claims before consequential actions, and avoid granting safety credit after a harmful action has already occurred. The same scenarios could also help an attacker reason about weaknesses in systems that over-trust signed artifacts or stale telemetry. To limit misuse, the evaluation is framed around controlled test cases and defensive design recommendations; it should not be connected to production systems or used to bypass real access controls. No personal data was collected or processed.

## Appendix B. Pre-Sprint Work Disclosure

A separate exploratory prototype, ProvenanceTrap, existed before the sprint (November 6–7, 2026) in https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11/provenancetrap. It contained an 8-case prompt-injection test and 96 Qwen2.5-3B runs. In the audited run, 22/96 tasks completed; 60 of the 76 failures halted immediately without tool interaction. The prototype did not include the cryptographic provenance or telemetry primitives evaluated here. This pre-sprint code and its runs are disclosed as prior work, not represented as sprint-created contributions.

Sprint work comprised the audit of that prototype; implementation of the HMAC-SHA256 keystore and telemetry discovery tools; construction of the 16-case benchmark; semantic grading and the 96-episode Qwen2.5-7B-Instruct run; trace auditing; and the version-2 action-ordering regrader. The new benchmark, experiment, traces, regraded results, and tests are in the submission branch.

## Appendix C. LLM Usage Statement

AI assistants were used to support literature discovery and summarization, code implementation and debugging, experiment-artifact inspection, analysis, and report editing. The author reviewed the cited sources, repository artifacts, raw execution traces, metric calculations, and final claims. AI-generated summaries or code outputs were not treated as experimental evidence without checking them against the underlying sources and artifacts.
