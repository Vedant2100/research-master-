<!-- Readable snapshot of the linked source document. The DOCX in this directory preserves original formatting. -->
Source: https://docs.google.com/document/d/1LrRCf8crBVCljb5nkpis7SB3N10L8g87/edit

# CS258 Design Doc: Learning to Write and Maintain Memory with RL

Nov 10, 2026 · @Vedant

This project trains a small memory model with RL to keep an agent's memory correct across sessions when sources conflict, go stale or are unreliable, rewarded only by a frozen reader's answers. Robustness to adversarial injections is measured as a secondary test.

## Motivation

Agents that keep memory across sessions must decide what to write: which updates supersede old facts, which sources to distrust, and what to refuse. In my audit of the FrontierMemory coding benchmark (45 trials per arm), generated memory did not beat no memory (19/135 vs 6/45; +0.01 per task, 95% CI −0.12 to +0.14), largely because the tasks left memory little room to help.

Two gaps motivate this project. First, Letta proposes memory models trained with downstream reward, but reports no experiments; RL-trained writers such as Memory-R1 and Mem-α exist, and Mem-α excludes conflict resolution. Second, memory poisoning is well benchmarked but defended statically: MemPoison finds write-time consistency checks stop direct attacks but not indirect ones, and calls for adaptive defenses. We ask whether a writer trained only on ordinary conflicts also resists injections, as a secondary robustness test.

## Environment: StaleStream

Each episode has 3–4 sessions of natural-language statements about 6–10 entity–relation slots, built from MQuAKE counterfactual edits. Each statement carries a source ID and an "as of" date. After every session the writer revises its memory without seeing earlier raw history, so memory is the only state carried forward. Five settings create headroom:

- Aliasing: subjects appear under different names and descriptions.
- Out-of-order delivery: arrival order differs from validity date.
- Unreliable sources: which sources are unreliable changes per episode and is never stated; later verified corrections give in-stream evidence.
- Adversarial injections: attacker sources insert false facts with authority claims, instruction-style payloads, and plants in session 1 that target questions asked only after session 4. Used for the robustness evaluation and one ablation; patterns follow MemPoison's attack types.
- Hard token budget: memory is cut off at 128–192 tokens.
After the final session the reader answers six questions: currently valid values, including slots targeted by attacks. Headroom is the gap between the oracle and the strongest non-privileged baseline.

## Method

The memory model is Qwen3-1.7B with LoRA. It reads each session plus its current memory and outputs revised free-text memory. A frozen Qwen3-4B reader answers from the final memory alone, in one call. Reward = mean exact match over the six questions. In one ablation run, trained with injections in 20% of episodes, reward also subtracts μ · (fraction of answers containing an injected value). Training methods; writer, reward and sampling budget are held fixed across 2 and 3:

- REINFORCE keep/drop controller over statement features with a leave-one-out baseline. An architecture baseline only: it selects facts instead of rewriting them.
- Best-of-N and rejection-sampling fine-tuning (RFT) on reader-ranked memories.
- GRPO and RLOO on the same writer (group size 8, about 300 steps each, matched sampling budget). Standard GRPO normalizes advantages by the group's standard deviation; RLOO uses a leave-one-out mean baseline without it. This is the main algorithm comparison. Credit is spread across the multi-session episode.
Course concepts: policy gradients, baselines and variance reduction, group-relative advantages, delayed credit assignment, imitation learning (RFT).

## Baselines and evaluation

Baselines: no memory, oracle, write-all, newest-wins, BM25 over all statements, prompted writers (Qwen3-1.7B and Qwen3-32B), one static write-time defense (prompted consistency check), a non-privileged symbolic resolver (alias normalization, timestamps, within-episode source scoring), and a privileged resolver given hidden labels.

Evaluation:

- 300 held-out episodes with disjoint entities, plus a shifted split, a shuffled-source split and held-out attack types.
- Utility (QA accuracy) is the main metric; attack success rate is reported on a held-out poisoned split.
- The training reader plus two held-out readers (Qwen3-32B and a model from another family), each against its own prompted-writer baseline.
- Memory factual correctness: whether each valid fact appears in memory and each injected value is absent.
- Zero-shot on real FactConsolidation-SH 6K.
- Paired bootstrap CIs, 3 training seeds, thresholds preregistered here, and a reader-exploitation check.
## Hypotheses

- H1: GRPO beats the strongest non-privileged baseline on utility, closing at least 50% of the gap to oracle.
- H2: At least 70% of that gain carries over to the held-out readers.
- H3: Robustness is measured, not assumed: on held-out attack types, a writer trained only on ordinary conflicts is compared with one trained with injections and with the static defense.
- H4: With writer, reward and budget fixed, GRPO and RLOO both beat RFT; their comparison shows whether std normalization changes stability or sample efficiency. Separately, the writer trained with RLOO beats the keep/drop controller trained with REINFORCE, which isolates the action space.
## Milestones

## Feasibility

Data. MQuAKE supplies thousands of counterfactual edit cases, and the generator recombines them, so training episodes are effectively unlimited; 300 GRPO steps need about 1,200–2,400. Held-out splits use disjoint entities. Attack payloads are templated from MemPoison's attack types rather than copied, since its cases target other memory formats.

Model competence. Two risks, both checked by the Nov 19 gate:

- Reader: counterfactual facts contradict the reader's pretrained knowledge, so Qwen3-4B may answer the real-world value even with correct memory. The oracle ≥ 90% gate measures this; if it fails, the reader moves to Qwen3-8B.
- Writer: 1.7B models follow memory-format instructions less reliably, and small models learn less reliably under RL. The writer gets a short warm start on best-of-N memories before GRPO.
Compute. 2× RTX 3090 (writer and reader), an existing Qwen3-32B server as held-out reader, Modal for burst runs, Colab for smoke tests. Multi-session episodes multiply writer generation by the number of sessions, so GRPO trains on 2-session episodes and is evaluated on 3–4. A single-session run is estimated at 5–10 hours, unmeasured until the Nov 19 timing test; three seeds may need Modal.

Timeline. FORGE (Nov 15) and Thanksgiving (Nov 26–27) take about 5 working days, leaving roughly 3 weeks of build and training. The gates exist so that a failure is found by Nov 24, not Dec 8.

## Optional extensions

Attempted only after the Nov 24 pilot passes, cheapest first. None is required for the core result.

- Continual vs offline weight updates (continual learning; Trajectory): train the writer on successive batches of unseen streams, updating the LoRA between batches, and compare with one offline run on the same data and step budget. Measure forgetting on earlier batches.
- Extra revision passes between sessions (Letta's sleep-time compute): let the trained writer revise its memory 1, 2 or 4 more times between sessions and plot accuracy against passes. Evaluation only, no new training.
- Longer horizons (long-horizon agents): evaluate on 10–20-session streams to find where memory quality starts to decay.
- One rollout per task (Trajectory): replace GRPO's group of 8 with a single sample plus self-distillation, using oracle memory as the privileged hint.
- Curriculum learning: train on simple revisions first, then add aliasing, unreliable sources and tighter budgets; compare with mixed training on the same budget.
Future work, not attempted here: attacker–writer self-play, recursive self-improvement of the training process itself, and agent execution trajectories as the writer's input.

## Scope, compute and deliverables

Deliverables: StaleStream as a reusable RL environment and eval suite (TRL-compatible reward, Hugging Face dataset, one-command baselines), the trained memory writers, and the IEEE report.

References: Letta memory models, Memory-R1, Mem-α, MemoryAgentBench, MemPoison, MPBench, MemComposer, MQuAKE (Zhong et al., 2023).

| Date | Milestone |
| --- | --- |
| Nov 19 | Headroom gate: oracle ≥ 90%; gap over the strongest non-privileged baseline ≥ 20 points. Thresholds do not move. Plus a 20-step end-to-end GRPO timing test. |
| Nov 24 | 100-step GRPO and RLOO pilots, and trained controller. If neither shows no learning signal, RFT becomes the main trained writer and the report says RL did not succeed. |
| Dec 1 | Injection-trained ablation run starts once the pilot has passed. |
| Dec 3 | Results freeze |
| Dec 10 | IEEE report, code and video |

| Risk | Mitigation |
| --- | --- |
| A symbolic resolver closes most of the gap | Add language difficulty before any RL; thresholds do not move |
| Reader ignores memory for pretrained knowledge | Oracle gate; larger reader |
| GRPO shows no learning by Nov 24 | RFT becomes the trained writer, reported honestly |
| Writer exploits the training reader | Two held-out readers and an exploitation check |
| Training slower than estimated | Fewer seeds, Modal burst, drop optional extensions |

| Area | Covered |
| --- | --- |
| RL post-training | Yes: GRPO and RFT on the writer's weights, REINFORCE controller |
| Memory | Yes: a trained memory model under conflict, staleness and budget, plus a secondary injection-robustness test |
| Continual learning | Yes: memory revised across sessions, as facts go stale |
| Self-improvement | No. Future work. |
