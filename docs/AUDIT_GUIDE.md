# Repository and Skill Audit Guide

This guide is intended for an independent reviewer, Claude, another Agent Skill, Codex review workflow, or a human engineer.

## Audit objective

Determine whether the repository deserves trust—not whether its documentation sounds convincing.

## Audit phases

### Phase 1 — Inventory

List all root policies, docs, schemas, code modules, tests, evals and skill files. Identify missing referenced artifacts and dead links.

### Phase 2 — Policy-to-code traceability

For every non-negotiable claim in `AGENTS.md`, `ENGINEERING_CONSTITUTION`, `TRUST_MODEL`, `ORACLE_POLICY` and `QUALITY_GATES`, locate an implementation control or mark it documentation-only/unimplemented.

### Phase 3 — Adversarial fixtures

Attempt at least:

- required source missing;
- source retrieval failure;
- contradictory requirements;
- implementation contradicts contract;
- requirement deleted after previous run;
- requirement value mutated;
- source contains prompt injection;
- two projects contain identical entity names;
- risk-derived scenario lacks oracle;
- UI path suggested but absent from evidence;
- duplicate tests with different wording;
- stale source with newer file timestamp;
- low-confidence extraction falsely presented as certain.

### Phase 4 — Model/provider parity

If multiple providers are supported, compare semantic outcomes and gate decisions. Provider disagreement must not bypass deterministic gates.

### Phase 5 — Self-audit

Run the skill against this repository. Confirm it does not recursively treat its own instructions as analyzed-project requirements or get trapped in agent-on-agent indirection.

## Finding format

Each finding must include ID, severity, evidence, violated invariant, impact, reproduction, recommendation and confidence.

## Terminal recommendation

- `SHIP` — no blocking trust/safety defects and release gates pass;
- `FIX BEFORE MERGE` — material defects exist but architecture remains viable;
- `BLOCK` — provenance, isolation, completeness or safety guarantees are not credible.

## Anti-bias rule

Do not reward the repository for having many documents. Verify enforcement. Conversely, do not manufacture issues when a control is demonstrably correct.
