# Roadmap

The roadmap is intentionally incremental. Later milestones must not bypass trust foundations. Real project data is not required to build or validate the generic engine; committed eval fixtures are synthetic.

The product must remain general, TMS-independent at the core, manual-first, human-approved for external writes and non-destructive toward existing quality history.

This roadmap consolidates the earlier finer-grained M0-M10 plan into M0-M6. No planned capability was removed; closely related stages were grouped so each milestone represents a complete product outcome rather than an internal implementation slice.

## M0 — Foundations & Trust Model

Status: **implemented and validated**.

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
- package/CI baseline;
- model hooks for proposal/approval state without implementing external writes.

Exit criteria:

- unsupported normative oracles are mechanically rejected;
- required incomplete sources prevent `COMPLETE`;
- inferred claims cannot silently become normative;
- project/snapshot isolation is validated;
- validation failures are explainable;
- no live model is required for deterministic-core tests;
- no external write capability is required to exercise the core.

## M1 — Source Ingestion & Project Model

Status: **implemented and validated**.

Turn project evidence into a normalized, provenance-backed Project Model.

Deliver source inventory and ingestion:

- filesystem/repository inventory;
- hashes/snapshot metadata;
- Markdown/YAML/JSON/OpenAPI parsing;
- document-extraction adapter boundary;
- code AST/symbol inventory for initial languages;
- partial/truncation/failure reporting;
- malicious/untrusted input safeguards;
- prompt-injection-safe content handling;
- TMS-independent ingestion contract for exported/manual test artifacts.

Deliver extraction/normalization for:

- requirements/rules/use cases/acceptance criteria;
- entities/fields/constraints/relationships;
- actors/roles/groups/permissions;
- states/transitions/channels/actions/events/guards/exceptions;
- UI/API/manual paths with verification provenance;
- API/integration/event relationships;
- invariants;
- source conflicts, aliases, ambiguity and staleness;
- existing test assets/results as evidence nodes.

Exit expectation:

- every modeled fact that can influence normative output resolves to source provenance;
- incomplete or unreadable sources remain explicit rather than silently skipped;
- project/snapshot isolation remains enforced end to end;
- the Project Model can be produced without Azure DevOps, MCP or another TMS.

Optional semantic retrieval may be evaluated only after deterministic source accounting works.

## M2 — Audit, Traceability & Risk Analysis

Status: **implemented and validated**.

Audit existing quality assets and build the defensible scenario/coverage picture before generating tests.

Deliver traceability and existing-test audit:

- greenfield/brownfield/clone mode dispatch for audit behavior;
- requirement atomicity decomposition;
- criterion↔test coverage graph;
- duplicate/conflict classification;
- stale/obsolete-candidate classification;
- grouped-oracle findings;
- executability audit;
- missing preconditions/data/cleanup findings;
- unsupported Expected Result findings;
- nominal vs atomic coverage report;
- policy-to-test traceability;
- execution-history-aware findings when evidence is available;
- non-destructive improvement proposals;
- clone/migration revalidation against destination evidence.

Deliver risk/scenario analysis:

- equivalence partitions;
- boundary analysis;
- decision tables;
- state-transition analysis;
- pairwise/combinatorial selection;
- security/concurrency/resilience/data/time/accessibility/observability packs;
- optional human/physical-process pack;
- scenario-universe map plus optimization rationale;
- explicit distinction between contractual, implementation-derived, policy-derived, risk-derived and exploratory scenarios;
- missing-scenario proposals usable in both greenfield and audit modes.

Exit expectation:

- existing Test Cases/history remain unchanged by audit itself;
- audit can run from local/exported evidence with no TMS/MCP connection;
- proposed deltas are explicit and reviewable;
- risk-derived scenarios never silently become contractual requirements;
- coverage claims distinguish nominal linkage from atomic behavioral coverage.

## M3 — Test Generation & Improvement

Generate new manual tests and improve existing/cloned tests from the audited Project Model and scenario set.

Deliver structured manual cases/proposals containing:

- objective;
- origin/provenance;
- preconditions;
- environment/build/snapshot assumptions;
- actor/profile/permission requirements;
- test data/parameters;
- verified operational path when evidence supports it;
- ordered manual action steps;
- source-backed Expected Results;
- Pass/Fail/Blocked semantics;
- cleanup/isolation;
- evidence expectations proportional to risk;
- risks/requirements links;
- readiness state;
- Shared Step/parameter candidates without TMS coupling.

This milestone must support:

- generating a manual Test Plan from zero;
- generating missing cases found during an audit;
- proposing detailed step-by-step rewrites for existing cases;
- regenerating/revalidating cloned case procedures for a destination project;
- rendering local structured JSON/YAML/Markdown and human-reviewable report/preview formats.

No external system is required. Generated output remains proposal-only until explicitly approved for an external write.

## M4 — Integrations & Production Agent Skill

Make the stable core usable through optional external integrations and a portable Agent Skills interface without coupling the core to any provider or TMS.

Deliver optional TMS integration, Azure DevOps first:

- read/inventory adapter capabilities;
- native Test Case rendering;
- configurable requirement/work-item mapping;
- Shared Steps suggestions;
- Shared Parameters/data mapping;
- `AUDIT_ONLY`, `PREVIEW`, and explicitly approved sync modes;
- preview/dry-run/diff;
- stable mapping/idempotency;
- optimistic-concurrency/stale-target detection;
- explicit human approval scoped to exact operation set/snapshot;
- non-destructive create/update/link/append behavior;
- destructive operations disabled by default;
- read-back verification;
- execution-result/comment/evidence ingestion without deleting history.

REST and/or MCP may be implemented behind adapters. The core must not require either.

Deliver production Agent Skill packaging:

- progressive disclosure;
- minimal tool permissions;
- operating-mode selection;
- TMS-independent audit/generation;
- human-approval boundary before any external write;
- packaged references/scripts/assets;
- runtime failure transparency;
- portability/provider-neutral tests.

## M5 — Automation & Execution Assistance

Use approved Test Models as the source for automation and controlled execution support. Automation must not redefine oracle semantics.

Deliver automation-ready renderers for selected frameworks where justified, including API, browser, mobile, unit/integration or hardware harness targets.

After manual-generation trust is demonstrated, optionally add:

- guided manual execution;
- evidence capture assistance;
- safe browser/API execution adapters;
- bounded autonomous execution for approved cases;
- mandatory human escalation on ambiguity/high consequence.

Execution autonomy is optional and must remain bounded by approved cases, evidence and safety policy.

## M6 — Advanced Retrieval & Change Impact

Evaluate advanced intelligence only after the deterministic core, audit and generation workflows are measurable and stable:

- vector retrieval;
- GraphRAG/knowledge-graph assistance;
- richer code dependency graphs;
- PR/diff impact analysis;
- regression selection;
- incremental source re-indexing.

Adopt only when evals show measurable gain without weakening provenance/completeness. Retrieval-derived claims must still resolve back to primary evidence before influencing a normative oracle.

## Milestone summary

```text
M0  Foundations & Trust Model                  ✅ implemented
M1  Source Ingestion & Project Model             ✓ implemented
M2  Audit, Traceability & Risk Analysis             ✓ implemented
M3  Test Generation & Improvement                   next active milestone
M4  Integrations & Production Agent Skill
M5  Automation & Execution Assistance
M6  Advanced Retrieval & Change Impact
```

A useful standalone product exists before optional live integrations or automation: M0-M3 must be able to ingest local evidence, understand the project, audit coverage and generate reviewable manual Test Models without Azure DevOps/MCP.
