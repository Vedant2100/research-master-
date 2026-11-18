# Install and invoke the paper-writing skill

The canonical skill is this `paper-writing/` directory. It uses the [Agent Skills](https://agentskills.io/specification) format and needs no runtime dependencies for its instructions. LaTeX, research-data and browser tools are optional task dependencies, not required for skill discovery. Version 0.2 also requires a plain-English definition and an authoritative clickable source for every specialized term on first use, including table captions and README files.

## Project-scoped use

In `research-master-` once this PR is checked out or merged:

- **Claude Code** discovers `.claude/skills/paper-writing/SKILL.md`. Request `/paper-writing` or describe a matching manuscript task.
- **Codex** discovers `.agents/skills/paper-writing/SKILL.md` at the repository root. Mention `$paper-writing` or ask to draft/review a manuscript. The Codex adapter reads the canonical skill, so both agents use the same rules.

The source-repo paper and research-agent configurations remain unchanged. Neither agent automatically edits a paper without a user task.

## Personal use across unrelated repositories

From the root of a checkout containing this skill:

```bash
mkdir -p "$HOME/.claude/skills" "$HOME/.agents/skills"
cp -R .claude/skills/paper-writing "$HOME/.claude/skills/"
cp -R .claude/skills/paper-writing "$HOME/.agents/skills/"
```

This copies the **full canonical folder**, not the short in-repo Codex adapter, so the references work in either personal location. The two copies will not stay synchronized automatically; copy again after updates or use your own versioned/symlinked setup.

## Example requests

- `/paper-writing Review the TrustVal manuscript against actual run traces; do not change experiment code.`
- `/paper-writing Edit this Results section for unnatural AI phrasing. Keep every figure, p-value and qualifier unchanged.`
- `$paper-writing Make a claim-to-evidence table and reviewer-style novelty critique before drafting an abstract.`
- `/paper-writing Finalize the PDF for the selected workshop using the official short-paper rules. Report exactly which checks ran.`

## Test after installation

Run the examples in `tests/smoke-cases.md`. The expected responses are specific, but the skill is an instruction workflow rather than a deterministic verifier; static YAML validation is not evidence that a model obeyed every rule.

## Prior work

Original skill instructions were written from observed paper-writing workflow. They **draw inspiration from**, but do not bundle or reproduce, [blader/humanizer](https://github.com/blader/humanizer) and [oaustegard/declauding](https://github.com/oaustegard/claude-skills). Those are optional separate tools.
