<!-- Readable snapshot of the linked source document. The DOCX in this directory preserves original formatting. -->
Source: https://docs.google.com/document/d/17jOimeZCTgH-18bdfjEmTVXh46eGe8GB/edit

# CS258 Project Proposal: Learning to Write and Maintain Memory with RL

## Problem

LLM Agents that work across sessions must decide what to keep in memory: which updates replace stale facts, which sources to trust, and what fits a fixed budget. Letta proposes training such memory models with downstream task reward. RL-trained writers such as Memory-R1 and Mem-α do not train on memory carried across sessions where facts go stale. In my audit of the FrontierMemory coding benchmark, generated memory gave no gain over no memory (+0.01 per task, 95% CI −0.12 to +0.14), largely because the tasks left memory little room to help. This project builds an environment where memory must matter and trains a writer in it.

## Environment: StaleStream

Each episode has 3–4 sessions of statements about 6–10 facts, built from MQuAKE counterfactual edits, each with a source and a date. After each session the writer revises its memory without seeing earlier raw history. Aliasing, out-of-order delivery, per-episode unreliable sources and a hard 128–192-token budget keep simple rules from solving it. A fixed reader LLM then answers six questions from the final memory.

## Method

The writer is Qwen3-1.7B with LoRA and outputs free-text memory. Reward is defined as a fixed Qwen3-4B reader's exact-match accuracy. The main comparison holds writer, reward and sampling budget fixed: GRPO (std-normalized group advantages) vs RLOO (REINFORCE with a leave-one-out baseline), with rejection-sampling fine-tuning (RFT) as the imitation baseline. A REINFORCE keep/drop controller is an architecture baseline: selecting facts vs rewriting them.

## Evaluation

Held-out episodes with disjoint entities, against no memory, oracle, newest-wins, a prompted Qwen3-32B writer and a symbolic resolver. Transfer to two readers never used in training. Zero-shot on FactConsolidation (MemoryAgentBench). Secondary: robustness to held-out adversarial injections (MemPoison-style), comparing a writer trained without injections, one trained with them, and a static consistency-check defense. 3 seeds, paired bootstrap CIs.

## Hypotheses

H1: RL closes at least 50% of the gap between the strongest non-privileged baseline and oracle. H2: at least 70% of that gain transfers to held-out readers. H3: GRPO and RLOO both beat RFT, and the rewriting writer beats the keep/drop controller.
