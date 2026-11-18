# Case notes from prior manuscript work

Use these as **methodological examples only**, not source data for an unrelated manuscript. Read the actual project sources if writing about these studies.

## FrontierMemory audit paper: restraint and editorial equivalence

The central scientific question was whether generated memory improved the same agent's performance over a no-memory control. The reported mean per-task effect was close to zero, with an interval that included both meaningful help and harm. The paper had to preserve that uncertainty; "memory does not work" would overstate the result.

Editing lessons:
- Describe how the memory was delivered, whether the agent actually opened it, and how the placebo was constructed; otherwise the comparison is hard to interpret.
- Separate source-code observations, measured data, and explanations of possible mechanisms.
- Do not call a commit-before-trials plan a **public preregistration** unless it was registered publicly.
- Preserve negative and contradictory evidence, task-specific successes, and infrastructure/verification issues.
- When removing prose that reads like an engineering log, retain enough detail to support reproducibility in the main paper or supplement.
- Review the whole paper for repeated "not X but Y" arguments. One good contrast is clearer than the same thesis in every section.
- Keep the IEEE page limit and double-anonymity requirements **only when that venue requires them**.

## TrustVal paper: benchmark construction and reviewer honesty

TrustVal evaluated agent decisions after ambiguous write responses. Its early benchmark leaked the outcome and deduplicated writes, so even unsafe retries could look correct. Later versions removed those confounds and produced failures in some older evaluated models; current models mostly saturated the test.

Writing lessons:
- Do not claim originality for a failure type already studied by larger prior work. Frame the actual engineering experience narrowly.
- The v2-to-v3 redesign changed multiple factors together. It shows an instrument problem; it is not a controlled one-variable ablation.
- State **exactly which outcomes the test injects**. A timeout after commit without a matched timeout after no commit does not test the full ambiguity decision.
- Distinguish the full manual run-ledger classification, independent spot checks of raw traces, all-run verifier checks, and direct SQL inspection. Those are different evidence levels.
- Report the small number of fixed tasks and repeated runs honestly; don't treat all task-trials as independent domains.
- Show a concrete failed retry and a concrete verified recovery from actual trajectories.
- A successful LaTeX build and visual PDF audit make a review draft; they do not establish scientific originality or that a paper was submitted.

## Rules extracted from both cases

1. The abstract must say **what changed under the measured comparison**, not what the authors hoped to demonstrate.
2. Exact task identity, unit of analysis, denominator and endpoint belong in the Results narrative.
3. A reader needs to understand the experimental environment, verifier and an entire real case.
4. Novelty comes from a concrete difference against closest work, not by relabeling known results.
5. Sentence-level humanization must not rewrite the study's claims, uncertainty, controls or caveats.
6. First complete the argument and evidence, then do the de-Clauding edit, then rebuild the exact source and read every rendered page.
