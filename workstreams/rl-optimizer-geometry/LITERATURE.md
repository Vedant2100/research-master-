# Fresh Related-Work Audit — 2026-11-17

| Work and primary source | What it shows | Implication for novelty |
|---|---|---|
| Rosić, *Hypergradient Descent on Muon*, Nov 2026, https://github.com/vukrosic/llm-research-paper-drafts/blob/d0dc052749a97061f6daa6907371bd0a2ec33405/02-muon-hypergradient-learning-rate/PAPER.md | Per author, 42/45 short tiny-LM settings within 0.005 of best swept constant LR using early adapt then hold; models no larger than 1.3M. | Exact code is a **reference**; no RL validation. |
| Baydin et al., *Online Learning Rate Adaptation with Hypergradient Descent* (2018), https://arxiv.org/abs/1703.04782 | Rate adaptation via hypergradients. | Gradient-based rate control is not new. |
| Amid et al., *Funnel* (2022), https://arxiv.org/abs/2202.00145 | Multiplicative exponentiated cosine update for rates. | Rosić explicitly acknowledges prior core rule. |
| Fan et al., *Rethinking Muon Beyond Pretraining*, May 2026, https://arxiv.org/abs/2605.19282 and official https://github.com/OPTML-Group/Pion | Muon may fail RLVR due to noisy spectral-tail amplification; proposes Pion high-pass and reports gains over Muon/AdamW in certain RLVR conditions. | Pion is mandatory baseline. |
| Ruan et al., *When Does Muon Help Agentic Reinforcement Learning?*, Jul 2026, https://arxiv.org/abs/2607.16169; https://github.com/x66ccff/verl-muon | ALFWorld Qwen2.5 0.5–3B GRPO/GiGPO/GraphGPO: some Muon gains, narrower when AdamW tuned or matched update sizes; exploratory comparisons may have limited independent seeds. | Strong LR, objective and applied-update controls are mandatory. |
| Crawshaw et al., *Muon and Its Many Variants*, ICML 2026, https://proceedings.mlr.press/v306/crawshaw26a.html | MuonMax and Momo improve robustness to hyperparameter choice. | Must avoid claiming generic robustness is novel. |
| *ISO: An RLVR-Native Optimization Stack*, Jul/Oct 2026, https://arxiv.org/abs/2607.19331 | Optimize singular frames while preserving pretrained spectral values. | Spectrum-preserving optimization is already explored. |
| *On the Policy Gradient Foundations of GRPO: Gradient Sparsity and Rank Collapse*, Jun 2026, https://arxiv.org/abs/2606.29238 | GRPO has low-rank/sparse gradient effects and credit-assignment implications. | A low-rank observation alone is not novel. |
| *Demystifying GRPO: Policy Gradient is a U-Statistic*, Mar 2026, https://arxiv.org/abs/2603.01162 | Finite-sample group-size/gradient variance analysis. | Group size/advantage estimator confound optimizer conclusions. |
| Mansouri et al., *Noise-corrected GRPO*, ICML 2026, https://proceedings.mlr.press/v306/mansouri26a.html | Handles explicit noisy rewards. | Must isolate reward corruption from optimizer-induced failures. |
| Huang et al., *Spectra: Rethinking Optimizers for LLMs Under Spectral Anisotropy*, ICML 2026, https://proceedings.mlr.press/v306/huang26d.html | Spectral anisotropy is a studied LM optimization issue. | Neither anisotropy nor SVD metrics alone are a discovery. |

## Remaining narrow question
Can a **prospective diagnostic from frozen, independently sampled policy-gradient halves** explain and predict optimizer performance on held-out RL tasks, after matching update RMS and tuning each optimizer fairly? This is a research hypothesis, not a verified novelty claim. Before writing a paper, refresh citations and compare against follow-up studies released after 2026-11-17.
