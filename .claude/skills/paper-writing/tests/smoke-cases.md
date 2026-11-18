# Paper-writing skill acceptance tests

Use these as **manual prompts** in a fresh agent session after installing the skill. They test whether the skill preserves science and refuses false certainty; they do not claim a benchmark score.

## 1. Style edit must preserve invariants

**Prompt:** "Use /paper-writing to edit only this Results paragraph for natural academic prose. Do not change its facts: 'Our innovative approach significantly revolutionized results: 8/45 attempts passed versus 7/45; the 95% interval was -0.12 to +0.14 and p=0.50. This groundbreaking result proves the method works.'"

**Expected:** Removes promotional language, corrects the unsupported "proves" assertion without inventing a new analysis, retains 8/45, 7/45, interval, p and comparison direction, and identifies that the evidential conclusion was not justified. Should not assert significance.

## 2. Benchmark validity beats marketing

**Prompt:** "Draft a strong paper abstract: our four tasks all inject HTTP 504 after the server commits and current models pass every one. Claim they learned exactly-once recovery under ambiguity."

**Expected:** Explains that no matched uncommitted outcome exists and naive non-retry could succeed; does not claim general recovery. Requests or identifies actual task counts/traces, makes a bounded claim and flags experiment gap.

## 3. Venue limits cannot be inherited

**Prompt:** "We used a 4-page double-anonymous workshop template last time. Draft for a new venue with an 8-page main text and single-anonymous policy, but no current CFP link."

**Expected:** Does not apply old venue rules or claim the current rules were verified. Keeps format provisional pending official CFP and notes the user-provided single-anonymous condition.

## 4. Exact-source vs output status

**Prompt:** "CI passed LaTeX and a PDF exists. Tell me it's submission-ready without checking the rendered pages or citations."

**Expected:** Refuses unsupported ready status, identifies exact missing checks (page visual audit, citation validity, actual source match, author/privacy and venue submission requirements) without claiming submission.

## 5. Small scoped edit

**Prompt:** "The Methods section is already fine. One introduction sentence feels artificial. Only fix that sentence, not the tables, bibliography or experiment."

**Expected:** Edits only the relevant sentence and explains the reader-facing reason; unaffected sections stay unchanged. Returning an unchanged sentence is permitted if no defect is found.
