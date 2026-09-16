# Roadmap

The roadmap is intentionally incremental. Later milestones must not bypass trust foundations. Real project data is not required to build or validate the generic engine; committed eval fixtures are synthetic.

The deferred hybrid semantic architecture and milestone ownership are cataloged in
`SEMANTIC_REASONING_ROADMAP.md`.

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

Status: **implemented and validated**. Evidence-backed multi-step authoring, strict readiness,
non-destructive brownfield/clone proposals, Shared Step/Parameter candidates, risk-proportional
evidence, canonical outputs, deterministic renderers and local CLI are complete. See
`M3_EVIDENCE.md`.

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

## M4 — Semantic QE & Production Agent Skill

Status: **active; H0-H4 and D1 validated, Technical Preview frozen before H5**. This local-first plan supersedes the earlier
M4 adapter allocation. Product positioning: **Evidence-first Quality Engineering runtime for AI agents.**
Agent reasons. Engine establishes what is defensible. Human governs high-consequence decisions.

Product experience priority is Agent Skill + AI agent first, `qe run`/`qe doctor` second, and the
deterministic trust engine as the shared foundation. Deterministic-only remains a valid fallback
and validation mode rather than the primary experience.

The cross-cutting `MULTILINGUAL_POLICY.md` applies to every milestone. M4.H3-H10 must treat PT-BR
and mixed PT-BR/English project material as first-class without pre-translation or authority drift.

Deliver a usable local, portable skill: evidence → deterministic extraction → bounded heuristics →
optional provider → candidate semantics → provenance/authority/trust → Project Model → audit/risk/
scenarios → Test Model → validation → clear human outputs. Confidence never grants authority.

### Checkpoints

- H0: scope/trust direction — complete.
- H1: provider-neutral bounded reasoning boundary — complete.
- H2: provenance-bound semantic candidates/cache — complete.
- H3: grounded multilingual normalization — complete, bounded capabilities documented.
- H4: semantic relations/conflicts and non-authoritative adjudication — validated; unsupported
  replacement/deployment links require review, never inferred from lifecycle alone.
- **D1: Technical Preview UX** — offline, self-contained HTML, PT-BR labels, full available case
  content, navigable provenance, visible conflicts/gaps/reviews, search/filter, responsive keyboard
  navigation and a reproducible synthetic demo. No frontend framework/server/CDN. Does not close M4.
- H5: real-world semantic ingestion with original text/span/locator, PT-BR/mixed inputs, minimal
  stale propagation and explicit unsupported formats; no mandatory translation/parser framework.
- H6: formal questions for missing evidence/authority, ambiguous rules, conflicts, unsupported
  oracles and unverified paths; bounded Scenario Grilling, never invented answers.
- H7: oracle quality/manual executability, preparation/data/steps/evidence/cleanup/isolation,
  optional faithful wording assistance; modality/polarity/conditions remain unchanged.
- H8: **local orchestration/output/export**, JSON/YAML/Markdown/HTML, locale, stable local run
  artifacts, validation before publication, no credential requirement or external write.
- H9: production runtime-neutral Agent Skill, `qe doctor`, `qe run <project>`, progressive
  disclosure, capability discovery, useful failures; deterministic-only mode fully valid.
- H10: whole-flow semantic/E2E evals, provider disagreement, mixed sources and mutations:
  deve→pode, pode→não pode, 30 s→60 s, antes→depois, somente ADMIN→qualquer usuário,
  até 10→no mínimo 10.
- H11: KISS hardening, packaging/install smoke/wheel/Linux/Windows, honest capability matrix,
  known limitations and local release evidence. No false production-ready claim.

Freeze after green D1 for presentation. **Do not start H5 automatically.** Use feedback before
continuing H5-H11. H9-lite is optional only after H4 and HTML are green and only if cheap/safe.

### M4 completion gate

Install → `qe doctor` → `qe run <project>` → source accounting/model/semantics/conflicts/questions/
audit/risks/scenarios/manual tests/validation/traceability/PT-BR HTML/Markdown/JSON. Thin agent
wrappers must not duplicate QE policy. Useful without Azure/Jira/TestRail/MCP/cloud credentials or
an LLM provider. Until M4 closes, call this **Technical Preview / MVP / v0.4.x**, not v1.0.0.

No live TMS connectors, CRUD, external approval execution/read-back or remote execution are
required or implemented in M4. Existing safety contracts remain binding; concrete adapters move
to M5. No vector DB, GraphRAG, swarm, microservices or speculative plugin platform.

## M5 — Automation & External Integrations

Execution priority: **after M6**, without renumbering historical IDs. Future adapters include
Azure DevOps/Jira/TestRail, preview/diff/sync, explicit exact human approval, optimistic concurrency,
idempotency and read-back. Preserve existing results/comments/evidence/history; destructive
operations remain disabled. REST/MCP are optional boundaries, never core dependencies.

Use approved Test Models as the source for automation and controlled execution support. Automation must not redefine oracle semantics.

Deliver automation-ready renderers for selected frameworks where justified, including API, browser, mobile, unit/integration or hardware harness targets.

After manual-generation trust is demonstrated, optionally add:

- guided manual execution;
- evidence capture assistance;
- safe browser/API execution adapters;
- bounded autonomous execution for approved cases;
- mandatory human escalation on ambiguity/high consequence.

Execution autonomy is optional and must remain bounded by approved cases, evidence and safety policy.

## M6 — Advanced Retrieval, Change Impact & Deep Audit

Execution priority: **immediately after M4, before M5**. Improve understanding of project changes
and affected requirements/tests before giving the system external execution capabilities.

Evaluate advanced intelligence only after the deterministic core, audit and generation workflows are measurable and stable:

- vector retrieval;
- GraphRAG/knowledge-graph assistance;
- richer code dependency graphs;
- PR/diff impact analysis;
- regression selection;
- incremental source re-indexing.
- requirement impact, stale artifact propagation and obsolete-test discovery;
- cross-language semantic drift and richer source/code dependency links.

Adopt only when evals show measurable gain without weakening provenance/completeness. Retrieval-derived claims must still resolve back to primary evidence before influencing a normative oracle.

## Milestone summary

```text
M0  Foundations & Trust Model                  ✅ implemented
M1  Source Ingestion & Project Model             ✓ implemented
M2  Audit, Traceability & Risk Analysis             ✓ implemented
M3  Test Generation & Improvement                   ✓ implemented
M4  Semantic QE & Production Agent Skill             active: H4 → D1 → freeze → H5-H11
M6  Advanced Retrieval, Change Impact & Deep Audit   after M4
M5  Automation & External Integrations               after M6
```

A useful standalone product exists before optional live integrations or automation: M0-M3 must be able to ingest local evidence, understand the project, audit coverage and generate reviewable manual Test Models without Azure DevOps/MCP.
