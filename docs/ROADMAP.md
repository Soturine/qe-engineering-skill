# Roadmap

The roadmap is intentionally incremental. Later milestones must not bypass trust foundations.

## M0 — Foundations & Trust Model

Deliver:

- repository governance and engineering constitution;
- source authority model;
- Source Ledger schema;
- claim/provenance and oracle schema;
- project/test model schemas;
- readiness states and quality gates;
- validator skeleton;
- baseline eval strategy;
- Agent Skill scaffold only.

Exit criteria: unsupported normative oracles and incomplete-source claims can be mechanically rejected in fixtures.

## M1 — Source Inventory & Parsing

Deliver:

- filesystem/repository inventory;
- hashes/snapshot metadata;
- Markdown/YAML/JSON/OpenAPI parsers;
- document extraction adapter boundary;
- code AST/symbol inventory for initial languages;
- source failure/status reporting;
- prompt-injection-safe content handling.

## M2 — Project Knowledge Model

Deliver extraction/normalization for:

- requirements/rules/use cases/acceptance criteria;
- entities/fields/constraints;
- actors/roles/permissions;
- states/transitions/channels;
- API/integration/event relationships;
- source conflicts, aliases and ambiguities.

Optional semantic retrieval can be evaluated after deterministic coverage exists.

## M3 — Traceability & Existing-Test Audit

Deliver:

- requirement atomicity decomposition;
- criterion↔test coverage graph;
- duplicate/conflict detection;
- obsolete-path and grouped-oracle findings;
- executability audit;
- coverage report that distinguishes nominal from atomic coverage.

## M4 — Risk & Scenario Engine

Deliver scenario universe generation using:

- equivalence partitioning;
- boundary-value analysis;
- decision tables;
- state-transition analysis;
- pairwise/combinatorial sampling;
- security/concurrency/resilience/data/time/accessibility packs;
- optional human/physical-process pack.

## M5 — Manual Test Case Generator

Deliver structured cases containing:

- objective;
- origin and provenance;
- preconditions;
- data;
- step actions;
- Expected Results;
- Fail/Blocked semantics;
- cleanup;
- risk and requirement links;
- readiness state.

## M6 — Azure DevOps Adapter

Deliver:

- native Test Case rendering;
- Shared Steps suggestions;
- Shared Parameters/test-data mapping;
- preview/dry-run/diff;
- explicit approval before bulk write;
- execution-result ingestion.

## M7 — Production Agent Skill

Turn the stable engine into a portable Agent Skills interface for Claude/Codex/Copilot-compatible environments. Keep instructions thin and enforce critical rules in validators.

## M8 — Automation-Ready Renderers

Render approved TestModel cases to selected frameworks (API, Playwright, Appium, pytest/JUnit, hardware harness). Automation must not modify oracle semantics.

## M9 — Advanced Retrieval & Change Impact

Evaluate:

- vector retrieval;
- GraphRAG for large multi-document projects;
- code dependency graph;
- PR/diff impact analysis;
- regression selection;
- incremental source re-indexing.

Adopt only when evals show measurable gain without weakening provenance/completeness.
