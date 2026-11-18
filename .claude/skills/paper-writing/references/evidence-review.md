# Evidence, skeptical review and publication verification

Use for planning, drafting, reviewing or finalizing any research paper. This is a **scientific audit**, not just grammar editing.

## Claim-to-evidence table

Maintain a working table outside the manuscript:

| Manuscript claim | Primary source | Evaluation unit and n | Qualification / discrepancy | Status |
|---|---|---|---|---|
| Mean difference is +0.02 | saved run summary, source SHA, analysis script | task-level mean, 12 fixed tasks, 3 seeds | CI overlaps zero; one failed run excluded by written rule | verified / open |
| Tool call generated duplicate | run ID, raw trace and database or verifier artifact | one executed episode | final prose may claim success; independent state must be checked | verified / open |

These are **illustrative fields and numbers only**, not findings to copy into a paper.

For each key result record:
- original protocol, version, run ID and run completion status;
- task/data sources, seeds/splits, independent unit, exclusions and all attempted arms;
- reward/verifier definition and whether the check is executable, model-judged, inferred from prose or manual;
- raw or locally regraded outcomes, with checks that they agree with submitted/hosted scores;
- estimator, confidence interval or test, with assumptions and multiple-testing concern;
- change history: pre-run design, later amendments, exploratory additions and post hoc comparisons;
- model, harness, tools, execution constraints and infrastructure failures as separate possible causes.

Distinguish a model score from an experiment **not run**. Never interpret ten repetitions of the same task as ten independent tasks. A missing verifier export must remain an audit gap even if an executive summary sounds certain.

## Skeptical reviewer questions

Answer before polishing an abstract:

1. **Contribution:** What is the nearest study? What exactly did they already do? Is the difference substantive or mostly an implementation format? Would the abstract still be true if you removed the novelty adjective?
2. **Construct validity:** Could a naive policy pass without the skill being tested? Does a failure necessarily mean the skill is absent? Does the reference solution trigger the challenged operation, or route around it?
3. **Missing counterfactual:** Are both branches of an ambiguous outcome tested? Are there matched non-faulted controls to distinguish generic task incompetence from recovery failure?
4. **Causal interpretation:** Did several things change at once? Were experiments chosen or revised after seeing results? Was the comparison truly controlled?
5. **Statistical unit:** Runs, seeds, tasks, agents or tool calls? Which are actually independent? Was the claimed p-value computed at the correct level?
6. **Comparability:** Are models using different wrappers, budgets, system prompts, serving paths, graders or network permissions? Did the benchmark change between arms?
7. **Negative findings:** Is the suite saturated? Are failures mostly infrastructure? Would a null result support "no detectable effect", or is it wrongly described as proof of equivalence?
8. **Reporting:** Were there invalid trials, timeouts, incomplete arms, stale dependency builds, unpinned datasets, missing raw artifacts, and partial reproductions?
9. **Evidence honesty:** Is each quote a real trace or an invented illustration? Does the source actually support the mechanism claimed? Are refs authentic, relevant, current and properly attributed?
10. **Reader comprehension:** Can a reader explain one entire episode from objective → API/action → fault → recovery → final state → verifier? If not, add a concrete example or diagram **from observed data**, not a fictional run.

If the closest prior art already establishes the central observation more rigorously, reposition as a bounded replication/tooling/evaluation case study **only if** that remains a real contribution. Otherwise recommend a technical report or additional research rather than cosmetic novelty.

## Before a manuscript is called ready

### Evidence
- All main numerical claims reproduced from source summary or script; table generation is deterministic and its diff reviewed.
- All study arms and sample sizes reported; no silently omitted failures.
- Text quotes match real logs; protocols match actual code and task versions.
- Sample-unit and uncertainty claims checked independently, not copied from a prose summary.
- Related-work novelty compared using full relevant sections of primary sources.
- No fabricated experiments, acceptance, preregistration, ethics approval, independent replication or statistical significance.

### Technical comprehension and links
- Every specialized term, acronym, metric, system/tool name and statistical method is explained in plain English on first use and linked to a primary source or official documentation.
- Acronyms are expanded; statistical terms explain the actual unit, comparison and interpretation.
- Captions define abbreviations locally; a reader can understand each table without hunting through the paper.
- Links resolve to the original paper, standard, official docs or the project's exact implementation, not an unrelated overview.
- Project-specific names are not presented as standard terminology; if no external source exists, the local meaning is stated and linked to the code/specification.

### Editorial
- Reverse outline has one coherent line from research question to conclusion.
- Abstract agrees exactly with table denominators, confidence intervals, limitations and model/tool versions.
- Terms defined on first use; figures/tables understandable without adjoining paragraph.
- No repeated thesis statements, generic transitions, overstated causality or promotional language.
- All material stylistic changes have a concrete reader benefit and preserve facts.

### Venue and build
- Official CFP and actual **track** checked for date, abstract and PDF deadlines, AoE vs local time, anonymity, format, references, appendix and archival status.
- Authors, affiliations, acknowledgments and artifact links comply with the actual anonymity policy.
- Bibliography sources and citation keys checked; no placeholder or non-existent source.
- Exact branch/commit source built using the required LaTeX/Word template; regenerated assets match committed inputs.
- **Each rendered PDF page** visually inspected for overlap, clipping, unreadable tables, floats, equations, bibliography and page number.
- Page count checked using the venue's rule about whether references count.
- Any sponsor/funding, AI assistance, ethics or dual-use statements checked against the venue rather than guessed.
- Submission, receipt or merging only after explicit user authorization.

## Output discipline

Mark check states precisely: **verified**, **checked by representative sample**, **based on a reported summary**, **blocked/unverified**, **not applicable**. Never collapse them into a single "all verified".

For a paper review report, give the top 3–5 blockers first, proposed precise changes, and any credible residual novelty risk. For an edit-only task, do not turn it into a research redesign unless an unsupported claim needs flagging.
