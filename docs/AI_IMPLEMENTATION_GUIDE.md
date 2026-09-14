# AI Implementation Guide

This guide exists so an implementation agent can continue the repository without relying on conversation history or a particular example project.

## Starting a task

1. Read `AGENTS.md`.
2. Identify the active roadmap milestone.
3. Read all normative docs relevant to that milestone.
4. Inspect the current tree, tests, schemas and ADRs.
5. Identify affected operating modes and trust invariants.
6. State the smallest coherent change that advances an exit criterion.
7. Implement code + tests + docs together.
8. Run deterministic validations and relevant evals.
9. Report exact status and remaining gaps.

## Product behavior that must remain possible

The generic engine must support, without requiring a TMS connector:

- greenfield Test Plan generation;
- brownfield/legacy Test Plan audit;
- clone/migration/reuse audit;
- later incremental regression/change-impact analysis;
- detailed manual step-by-step Test Model generation or rewrite proposals in any relevant mode.

The design must remain project/domain neutral. Prior projects may inform heuristics, but never become hidden normative truth.

## Human approval boundary

Generation, auditing and rewriting are proposal-producing operations.

No external CRUD is implied by model output. Any future external create/update/link/append operation requires explicit human approval scoped to the exact proposal, target and snapshot. Destructive operations remain disabled by default.

Existing Test Cases, requirements, runs/results, comments, screenshots/attachments, bug links and historical evidence must be preserved by ordinary audit/sync behavior.

## Current directive: build M0 first

Do **not** begin by implementing a fluent test-case generator.

Implement in this order:

1. package/tooling/CI;
2. schemas;
3. typed/validated domain contracts;
4. Source Ledger + Run Manifest;
5. oracle/provenance validators;
6. completeness/readiness/approval validators;
7. Project Model skeleton compatible with future greenfield/brownfield/clone modes;
8. synthetic hard-invariant evals;
9. minimal CLI for real validators;
10. only then advance to M1.

See `docs/IMPLEMENTATION_SPEC.md` and `docs/CODEX_M0_TASK.md`.

## Do not jump ahead

Do not build a sophisticated generator, RAG stack, GraphRAG, bulk TMS writer, Azure/MCP dependency or autonomous browser execution before M0/M1 invariants can be tested. Fluent output on weak trust foundations is a regression, not progress.

## Language-model use

Use models for semantic extraction from unstructured text, relation/alias proposals, contradiction candidate detection, scenario ideation, wording after an oracle exists and risk brainstorming.

Prefer deterministic code for inventory/scope accounting, hashes/version identity, schema validation, code symbols/imports where parsers exist, duplicate IDs, gate transitions, output limits, source→claim→oracle linkage, project/snapshot isolation and approval-scope validation.

Core tests must not require a live model.

## Provider adapters

Never scatter provider calls through domain code. Use typed request/result interfaces. Provider output must be schema-validated, include provider/model/version metadata when material, retain source span/symbol references and never bypass deterministic gates.

## Model/prompt changes

Treat provider/model/prompt/extraction changes as dependency changes. Re-run relevant evals and record the change before declaring semantic parity.

## Fixtures

Committed fixtures are synthetic/generic. They encode defect classes and operating-mode patterns, not real project rules.

Useful synthetic fixture families include:

- greenfield project with no tests;
- brownfield project with partial/duplicated/stale tests;
- clone/reuse project with conflicting old assumptions;
- project with missing/blocked sources;
- project with ambiguous oracles and risk-only scenarios.

## Documentation discipline

A future coding agent must be able to reconstruct architectural intent from the repository alone. If implementation relies on an unwritten conversational assumption, the change is incomplete.
