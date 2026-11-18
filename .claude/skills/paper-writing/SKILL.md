---
name: paper-writing
description: Plan, draft, edit, audit, and finalize scientific papers, workshop submissions, abstracts, and rebuttals. Use for academic manuscript writing, paper review, "declauding", "humanize this paper", venue-fit checks, claim-to-evidence checks, or LaTeX/PDF submission preparation. Keeps the user's actual experiments and voice intact while removing formulaic AI prose and checking novelty, evidence, statistics, citations, and page limits.
metadata:
  version: "0.1.0"
---

# Paper writing

Produce a readable, defensible research manuscript from **what was actually done**. Research correctness takes priority over polish. A style edit never authorizes a scientific edit.

## Core rules

1. **Do not invent** experiments, baselines, results, citations, run counts, significance, methods, model versions, approvals, or submission status. Distinguish designed, implemented, executed, verified, submitted, and accepted.
2. **Preserve scientific invariants.** Keep all numbers, units, denominators, confidence intervals, test definitions, seeds, splits, qualified claims, citations, equations, code, and LaTeX macros unchanged unless a source-backed correction is explicitly justified.
3. **Read before editing.** Read the whole draft, relevant repository files, run ledger, protocol, and existing PR diff before proposing prose edits. When the user asks for a limited pass, do not rewrite unrelated sections.
4. **No invented novelty.** Compare directly with the nearest published/preprint work. A useful negative result or engineering case study is legitimate, but it must be described as such.
5. **The venue wins.** Verify the specific current CFP/track and its length, format, anonymity, references, appendix, artifact, ethics, AI-assistance, dual-submission and deadline rules. Do not inherit another conference's template.
6. **Human voice, academic register.** Remove mechanical writing patterns because they obscure the argument, not to fool AI detectors. Preserve legitimate hedging, Methods passive voice where appropriate, technical terminology, and the author's distinctive wording.
7. **Never self-certify.** A green CI check is not an experiment; a successful LaTeX command is not a visual PDF review; a draft PR is not a submission. No merge or external submission without authorization.


## Technical terms must be explained and linked

This is a **hard publication-readability rule**, not an optional polish pass:

- On first use, every specialized technical term, acronym, metric, protocol, tool/framework name, statistical procedure, and domain-specific phrase must be explained in ordinary language **and linked** to a reliable source.
- Use the pattern: **term** + a short explanation of what it means in this paper + a clickable link to the best source. A link alone is not an explanation; an expansion of an acronym alone is not an explanation.
- Prefer primary sources: official technical documentation or standards for protocols and tools; the original paper or official project page for methods and benchmarks; the actual repository implementation for project-specific behavior. Avoid generic search-result pages and low-quality glossaries.
- For a project-specific term with no external definition, explain the local meaning and link to the relevant code, task specification, or experiment record. Never imply that an implementation-specific label is a field-wide standard.
- Expand acronyms on first use. Explain unfamiliar statistical language in terms of the actual analysis unit and comparison. Define abbreviations and symbols in tables/captions as well as in the main text when a reader could encounter the exhibit first.
- Do not attach links to every repeated occurrence. Define and link at first use, then use the term consistently. In a short paper, prefer concise parenthetical explanations or a compact linked glossary over bloated exposition.
- If no trustworthy explanatory link exists, replace the term with plain language or state the local definition and link to the project's own source. **Do not leave it unexplained.**
- Audit the title, abstract, body, tables, figure captions, footnotes, README, and supplementary instructions. A reader should not need to search independently to decode the paper.

## Choose the requested mode

- **Plan:** Give research questions, defensible contribution, venue fit, closest prior art, proposed structure, evidence gaps, page budget and go/no-go criteria. Do not silently create results.
- **Draft:** Write a real manuscript grounded in a claim ledger. Prefer a concrete motivating example and an explicit measured question over broad motivational slogans.
- **Edit / de-Clauding / humanize:** Preserve the scientific content. Scope edits to passages with a concrete reader-facing problem. Consult [editing.md](references/editing.md).
- **Review:** Act as a skeptical peer reviewer: novelty, construct validity, controls, sample units, baseline fairness, reporting gaps, alternative interpretations and hard reviewer objections. Consult [evidence-review.md](references/evidence-review.md).
- **Finalize:** Reconcile exact source, regenerated figures/tables, citations and target venue; compile and inspect every PDF page. Keep a clear list of unresolved gates.

If the user supplies several modes, do them in order. If the mode is unspecified, begin with a quick evidence/novelty audit before writing polished prose. For an existing draft, use its current branch/PR rather than opening parallel versions by default.

## End-to-end sequence

### 1. Lock the submission contract

Read the official CFP, **specific track** and author instructions. Record the date checked; exact abstract/full-paper deadlines and timezone; page limit (including or excluding references); template; anonymity; publication and dual-submission rules. If the venue is undecided, use a neutral manuscript structure and mark format as provisional.

### 2. State the honest thesis

In plain language write: (a) the question, (b) what was built or measured, (c) the actual outcome, (d) the specific difference from the closest work, (e) the principal limitation. Read the **full methods/results** of close papers, not just titles or abstracts. If contribution strength is weak, say so before investing in cosmetic rewriting.

### 3. Construct a claim-to-evidence map

For every key sentence or figure, capture the repository/commit, dataset/task version, actual run IDs, evaluation procedure, denominator, statistical unit, source table or trace, and limitations. Keep infrastructure failures, oracle/control scores, exploratory trials and independent model trials separate. A design document is not evidence of an executed experiment.

Generate quantitative tables from raw or verified aggregate data when feasible. Never tweak counts in LaTeX by hand. Define what a pass, failure, success rate, comparison and p-value mean. Check whether repetitions are independent or reuse the same fixed tasks.

### 4. Structure the argument before polishing

Draft Methods and Results from evidence, Discussion from supported interpretations, then Introduction and Abstract. Use a reverse outline: each paragraph should have a job and change what the reader knows. Explain abbreviations and technical objects at first use. Introduce each result with the question it answers and an explicit comparison. Negative results and saturation belong in the main story when they determine interpretation.

An effective short paper often uses: concrete failure or question → prior-work gap → artifact/protocol → controls → measured results → what cannot be inferred → implication. Adapt to genre; do not force a template onto an unrelated experiment.

### 5. Perform a scoped human-language edit

Read [editing.md](references/editing.md). Identify actual problems: repeated thesis, symmetrical section openings, generic significance claims, fake contrast formulas, transition fillers, dense citation inventories, and overcompressed method descriptions. For **each** material edit, be able to say why the reader benefits. Delete duplicated rhetoric before paraphrasing. Prefer direct verbs, specific subjects and varied natural cadence.

When installed, `declauding` and `blader/humanizer` may be consulted as **diagnostic passes**, not as authorities over facts or publisher style. Do not copy their full rule catalogs into this skill. No mechanical synonym swaps, fabricated personality, or universal prohibition on valid academic constructions.

### 6. Challenge the science

Read [evidence-review.md](references/evidence-review.md). Attempt to disprove the main claim. Ask whether the verifier measured the intended construct; whether a naive workaround passes; whether the oracle actually hits the fault; whether a matched counterfactual is missing; whether edits were post hoc; whether comparisons are confounded by harness or model; whether the conclusions apply only to the tested tasks.

If an objection stands, correct the claim or prominently disclose the limit. Do not add an unexecuted experiment as though performed.

### 7. Exact-source release gate

Reconcile the working manuscript with the committed source and generated results. Check BibTeX entries against actual scholarly sources and citation keys against the document. Compile with the venue's real template; check page count **including references if required**. Render **every** page and inspect figures, tables, overflow, fonts, headings, orphaned floats, bibliography, citations, author placeholders and anonymity.

If you did not execute a check, say **not checked**. A local mirror is not automatically a clean-clone build. A final PDF is a review artifact, not submission evidence. Do not submit or merge without explicit approval.

## Deliverables

Return the manuscript/diff and a concise status: **verified facts**, **editorial decisions**, **open scientific risks**, **format/build checks actually run**, and **what still blocks submission**. For substantial edits, retain a compact edit ledger of passage → problem → change → fact-preservation check. Do not dump long self-praise or generic checklists into the paper.

Read [evidence-review.md](references/evidence-review.md) for the ledger and reviewer pass. Read [case-notes.md](references/case-notes.md) only when an example of the workflow helps. Both are general lessons from prior papers, not facts to import into a new paper.

## Scope of this skill

This is an original orchestration skill informed by prior de-Clauding and Humanizer usage, plus real manuscript audits. It does not vendor their copyrighted instructions or require their installation. It cannot replace actual experiments, source verification or independent peer review.
