# ProvenanceTrap Eval Agent

**Area:** Alignment & Agent Safety
**Source:** https://github.com/Vedant2100/role-work-forge-artifacts/tree/main/hackathons/2026-11
**Owner agent:** `provenancetrap`
**Current agent state:** CONFIGURED, NOT YET DISPATCHED (no active session or actual model run assumed)

## Research aim
Measure authorized task completion while rejecting instructions from lower-trust files/tools.

## Next decisive action
Use a stronger tool-capable model, fix completion floor and rerun matched benign/adversarial cases.

## Experimental gate
Nontrivial legitimate completion, frozen verifier, explicit unauthorized reads/writes and repeatable tasks.

## Do not overclaim
A model that quits immediately is not safe. micro1 deadline missed; no verified submission.

## Evidence handoff
No master-repo independent agent handoff yet. After dispatch, include immutable source commits, commands, exact per-episode evidence, model results, matched comparisons, blockers, costs and PR links here.
