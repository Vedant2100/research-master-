# Academic prose editing: de-Clauding without losing science

Apply this file after the scientific draft and evidence map exist. The goal is deliberate research prose, not AI-detector evasion or artificially casual language.

## How to decide whether to edit

Read the **whole section** first. Find the actual reader problem. For each proposed change ask:

1. What does the passage need to communicate?
2. What is confusing, redundant, inflated or oddly staged in the current wording?
3. Does the edit improve that problem while preserving **every** scientific detail?
4. Is the existing sentence already adequate? If yes, leave it alone.

Do not perform a global rewrite just because a heuristic detects a word. A style edit changes delivery, not research content.

## High-value patterns to inspect

| Problem | Better intervention |
|---|---|
| "Not X but Y" repeated in abstract, intro, results and conclusion | State the actual measured fact once, then make subsequent sections advance the argument. Contrast only when a misconception genuinely matters. |
| Generic opener: "In the rapidly evolving landscape of..." | Start with the concrete tool, failure, observation or research question. |
| Every paragraph starts "We evaluate", "We find", "This highlights" | Vary structure to reflect different intellectual jobs; do not force cosmetic variety where parallelism helps. |
| Significance inflation: "critical, groundbreaking, transformative, robust" | Replace with the specific supported comparison, consequence or boundary. |
| Two sentences repeat the same conclusion after the table | Keep the sentence that interprets the evidence; delete the sales-like restatement. |
| Citations stacked in a semicolon-heavy inventory | Group by real conceptual distinction and explain how the current work differs. Verify each reference first. |
| Heavily compressed Methods sentence with undefined terms | Split the procedure into actor, action, environment, metric and limitation. Define a term on first use. |
| Artificial triads and symmetrical bullet/section structures | Keep parallelism when logically required. Otherwise follow the actual conceptual hierarchy rather than filling three slots. |
| Overloaded dash interruptions or dash-as-transition | Prefer a period, comma or parenthesis where clarity improves. Avoid em/en dashes in user-facing prose unless the venue or quotation requires them. Do not corrupt mathematical minus, code, compound names or numeric ranges. |
| Generic conclusion: "Together, these findings underscore the importance..." | State what was observed and precisely what it supports or does not support. |

## Technical language and links

Never equate natural prose with removing technical vocabulary. Keep the precise term when it is needed, but explain it at first use and attach a clickable primary-source link. For example: "an idempotent request (repeating it has the same effect as sending it once; [API retry guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/))." A hyperlink without a plain-language explanation is insufficient. If the term describes this project's own implementation, explain it and link to the exact code or task definition. Check captions and README files too.

## Tiny original examples

**Before:** "Importantly, this is not merely a timeout problem, but a fundamental challenge to agent reliability."

**After:** "The timeout returned after the first write committed. The agent repeated the write and created a duplicate."

Why: concrete operation and consequence replace abstract emphasis. Do **not** use this example when the recorded trace does not show a commit.

**Before:** "We preregistered the protocol."

**After, only when supported:** "We committed the analysis plan before running the reported trials."

Why: a Git commit before the runs is an auditable plan, but it is **not** necessarily a public preregistration. Preserve exact timestamp and any amendments where needed.

**Before:** "Our benchmark demonstrates that newer models are safe."

**After, only when supported:** "The tested models passed nearly all trials on these four fixed scenarios."

Why: the denominator and scope govern the claim; passing a small suite does not establish general safety.

## Academic register overrides

- Methods may use passive voice when it is clearer or conventional. Do not force artificial "we" sentences.
- Keep epistemic uncertainty: "is consistent with", "may", and "does not establish" are appropriate when warranted. Trim only stacked or pointless hedges.
- Keep the publisher's heading capitalization, math, citation punctuation, names, and LaTeX conventions. Generic humanizer rules do not override publication requirements.
- Match the author's previous writing if available. Do not add fictitious first-person experiences or anecdotes.
- Paper prose should not include internal project planning chatter, GitHub PR status, reviewer self-talk, filler audit prose, or promises of future work disguised as accomplished results.
- Preserve technical terms. Explain unfamiliar terms rather than replacing them with weaker colloquialisms.

## Mandatory post-edit equivalence check

Compare edited passage to its source. Look for silently changed:

- counts, model labels, denominators, dates, confidence intervals, p-values and significance;
- causal strength, comparison direction, quantifiers ("all", "some", "only");
- negative results and failed attempts;
- controls, ablations, protocols, baselines, sample dependencies and limitations;
- citation attachment, quotes, code, formulas, LaTeX labels and generated tables.

If an apparent factual error is found, put the proposed correction in the claim ledger with its source instead of quietly folding it into a style pass.

## Edit log (when working in a repository)

Use a brief ledger, not a prose-by-prose autobiography:

| Passage | Reader problem | Justified edit | Invariants rechecked |
|---|---|---|---|
| Intro, paragraph 2 | repeats the abstract's claim | replaced with motivating example | outcome, source, scope unchanged |
| Methods, paragraph 1 | undefined "sidecar" | added one definition | architecture and access boundaries verified |
| Discussion, final line | unjustified generalization | limited conclusion to tested tasks | denominator and failure cases checked |

No edit required is a valid outcome. Never say "humanized" merely because a linter found zero terms.
