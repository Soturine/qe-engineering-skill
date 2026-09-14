# Roadmap

The roadmap is intentionally incremental. Later milestones must not bypass trust foundations. Real project data is not required to build or validate the generic engine; committed eval fixtures are synthetic.

## M0 — Foundations & Trust Model

Deliver:

- repository governance and engineering constitution;
- source authority policy;
- Project Input Contract;
- Source Ledger schema;
- run manifest/snapshot schema;
- claim/provenance and oracle contracts;
- Project Model/Test Case/Risk schemas;
- readiness/completeness states;
- deterministic validators for hard trust invariants;
- synthetic eval harness/fixtures;
- Agent Skill scaffold only;
- package/CI baseline.

Exit criteria:

- unsupported normative oracles are mechanically rejected;
- required incomplete sources prevent `COMPLETE`;
- inferred claims cannot silently become normative;
- project/snapshot isolation is validated;
- validation failures are explainable;
- no live model is required for deterministic-core tests.

## M1 — Source Inventory & Parsing

Deliver:

- filesystem/repository inventory;
- hashes/snapshot metadata;
- Markdown/YAML/JSON/OpenAPI parsing;
- document-extraction adapter boundary;
- code AST/symbol inventory for initial languages;
- partial/truncation/failure reporting;
- malicious/untrusted input safeguards;
- prompt-injection-safe content handling.

## M2 — Project Knowledge Model

Deliver extraction/normalization for:

- requirements/rules/use cases/acceptance criteria;
- entities/fields/constraints;
- actors/roles/permissions;
- states/transitions/channels;
- UI/API paths with verification provenance;
- API/integration/event relationships;
- source conflicts, aliases, ambiguity and staleness.

Optional semantic retrieval may be evaluated only after deterministic source accounting works.

## M3 — Traceability & Existing-Test Audit

Deliver:

- requirement atomicity decomposition;
- criterion↔test coverage graph;
- duplicate/conflict classification;
- obsolete-path/grouped-oracle findings;
- executability audit;
- nominal vs atomic coverage report;
- policy-to-test traceability.

## M4 — Risk & Scenario Engine

Deliver:

- equivalence partitions;
- boundary analysis;
- decision tables;
- state-transition analysis;
- pairwise/combinatorial selection;
- security/concurrency/resilience/data/time/accessibility/observability packs;
- optional human/physical-process pack;
- scenario-universe map plus optimization rationale.

## M5 — Manual Test Case Generator

Deliver structured manual cases containing:

- objective;
- origin/provenance;
- preconditions;
- test data;
- operational action steps;
- source-backed Expected Results;
- Pass/Fail/Blocked semantics;
- cleanup;
- risks/requirements links;
- readiness state;
- Shared Step/parameter candidates without TMS coupling.

## M6 — Azure DevOps Adapter

Deliver:

- native Test Case rendering;
- Shared Steps suggestions;
- Shared Parameters/data mapping;
- preview/dry-run/diff;
- idempotent create/update mapping;
- explicit approval before bulk writes;
- execution-result ingestion.

## M7 — Production Agent Skill

Turn the stable engine into a portable Agent Skills interface for compatible runtimes:

- progressive disclosure;
- minimal tool permissions;
- packaged references/scripts/assets;
- runtime failure transparency;
- portability/provider-neutral tests.

## M8 — Automation-Ready Renderers

Render approved Test Models to selected frameworks (API, browser, mobile, unit/integration, hardware harness). Automation must not redefine oracle semantics.

## M9 — Advanced Retrieval & Change Impact

Evaluate:

- vector retrieval;
- GraphRAG/knowledge-graph assistance;
- richer code dependency graphs;
- PR/diff impact analysis;
- regression selection;
- incremental source re-indexing.

Adopt only when evals show measurable gain without weakening provenance/completeness.

## M10 — Controlled Execution Assistance (optional)

Only after manual-generation trust is demonstrated:

- guided manual execution;
- evidence capture assistance;
- safe browser/API execution adapters;
- bounded autonomous execution for approved cases;
- mandatory human escalation on ambiguity/high consequence.

Execution autonomy is an optional later capability, not a prerequisite for the core skill.
