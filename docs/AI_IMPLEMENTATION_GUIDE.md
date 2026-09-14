# AI Implementation Guide

This guide exists so an implementation agent can continue the repository without relying on conversation history or a particular example project.

## Starting a task

1. Read `AGENTS.md`.
2. Identify the active roadmap milestone.
3. Read all normative docs relevant to that milestone.
4. Inspect the current tree, tests, schemas and ADRs.
5. State the smallest coherent change that advances an exit criterion.
6. Implement code + tests + docs together.
7. Run deterministic validations and relevant evals.
8. Report exact status and remaining gaps.

## Current directive: build M0 first

Do **not** begin by implementing a fluent test-case generator.

Implement in this order:

1. package/tooling/CI;
2. schemas;
3. typed/validated domain contracts;
4. Source Ledger + Run Manifest;
5. oracle/provenance validators;
6. completeness/readiness validators;
7. synthetic hard-invariant evals;
8. minimal CLI for real validators;
9. only then advance to M1.

See `docs/IMPLEMENTATION_SPEC.md`.

## Do not jump ahead

Do not build a sophisticated generator, RAG stack, GraphRAG, bulk TMS writer or autonomous browser execution before M0/M1 invariants can be tested. Fluent output on weak trust foundations is a regression, not progress.

## Language-model use

Use models for semantic extraction from unstructured text, relation/alias proposals, contradiction candidate detection, scenario ideation, wording after an oracle exists and risk brainstorming.

Prefer deterministic code for inventory/scope accounting, hashes/version identity, schema validation, code symbols/imports where parsers exist, duplicate IDs, gate transitions, output limits, source→claim→oracle linkage and project/snapshot isolation.

## Provider adapters

Never scatter provider calls through domain code. Use typed request/result interfaces. Provider output must be schema-validated, include provider/model/version metadata when material, retain source span/symbol references and never bypass deterministic gates.

Core tests must not require a live model.

## Model/prompt changes

Treat provider/model/prompt/extraction changes as dependency changes. Re-run relevant evals and record the change before declaring semantic parity.

## Fixtures

Committed fixtures are synthetic/generic. They encode defect classes, not real project rules.

## Documentation discipline

A future coding agent must be able to reconstruct architectural intent from the repository alone. If implementation relies on an unwritten conversational assumption, the change is incomplete.
