# QE Engineering Skill

Evidence-first, manual-first quality engineering for software, APIs, mobile, data, IoT and industrial systems.

This repository defines a vendor-neutral Agent Skill plus a supporting deterministic engine for **understanding a project from its actual evidence, auditing existing quality assets, mapping behavior and risk, and generating high-confidence manual test cases with explicit provenance**.

Automation is a later renderer of the same approved Test Model. It is not the starting point and must never redefine oracle semantics.

## Core principles

> **No normative Expected Result without a traceable oracle. No claim of completeness without a verifiable source inventory. No silent inference. No destructive history rewrite. No external write without explicit human approval.**

The objective is not to maximize the number of tests. It is to build the smallest defensible, executable test set that covers relevant behavior and risk, while explaining why every normative expectation exists.

## What the skill is intended to do

The system is designed to work across different project maturity levels. It may analyze, when available:

- PRDs/product specifications;
- functional and non-functional requirements;
- business rules;
- use cases and acceptance criteria;
- ADRs and technical decisions;
- source code and repository history;
- pull requests/diffs;
- database models and migrations;
- API/event/data contracts;
- UI/design/manual/runbook evidence;
- configuration and feature flags;
- automated tests;
- manual Test Cases/Test Plans;
- execution results;
- comments, screenshots/attachments and linked bugs/issues;
- integration and operational documentation;
- security/quality/engineering policies.

It then builds an evidence-backed internal model of the project before producing or modifying any test proposal.

## How project understanding works

The target flow is:

```text
explicit scope
    ↓
deterministic source inventory
    ↓
source identity / snapshot / integrity
    ↓
parsing + AST/symbol extraction
    ↓
source authority + provenance + conflict detection
    ↓
normalized Project Model
    ↓
requirement atomicity + existing-test audit
    ↓
risk / scenario universe
    ↓
coverage optimization + duplicate classification
    ↓
manual Test Model
    ↓
quality gates
    ↓
human review / approval
    ↓
optional renderer/export/TMS publication
```

The Project Model is intended to represent, when applicable:

- entities, fields, relationships and constraints;
- actors, roles, groups and permissions;
- states, transitions, actions/events, guards, exceptions and channels;
- requirements and atomic criteria;
- invariants;
- interfaces, APIs, queues, events and integrations;
- configuration/environment dependencies;
- UI/API/manual paths only when verified;
- ambiguities, aliases and conflicts;
- risks and scenarios;
- existing tests/results;
- atomic coverage relationships;
- generated Test Models.

Every semantic node that can influence a normative test must retain provenance.

## Operating modes

The engine is intentionally general and must not depend on one project, domain or TMS.

### 1. Greenfield Test Design

Use when project evidence exists but there is no meaningful manual Test Plan yet.

```text
project evidence
→ Project Model
→ atomic criteria
→ risks/scenarios
→ optimized coverage
→ manual Test Cases from zero
→ review
```

The generated plan is only as authoritative as the available evidence. Missing code means implementation alignment cannot be claimed; implementation-only evidence does not silently become business contract.

### 2. Brownfield / Existing Test Plan Audit

Use when requirements/tests/executions already exist.

The system audits before proposing changes and can identify:

- nominal versus atomic coverage gaps;
- missing scenarios;
- vague or non-executable steps;
- grouped independent validations;
- unsupported Expected Results;
- missing preconditions/data/cleanup;
- stale paths, actors, roles, states or assumptions;
- duplicate or conflicting tests;
- security/concurrency/recovery/boundary gaps;
- recurring Fail/Blocked patterns;
- opportunities for Shared Steps/parameters;
- missing links and traceability.

It may propose a detailed new step-by-step version of an existing case, but the existing asset remains unchanged until a human explicitly approves an external update.

### 3. Clone / Migration / Reuse Audit

Use when a previous Test Plan or requirement set is reused as a starting point.

Cloned content is historical evidence, not truth for the destination project. The engine revalidates old assumptions against current project evidence and may classify each asset as reusable, needing update, conflicting, duplicate, obsolete candidate, untraceable or unknown.

Old oracles, UI paths, roles, statuses and data are never copied blindly into the destination project.

### 4. Incremental Change / Regression Audit

Later, a trusted baseline can be compared with a new PR, commit or requirement change to identify impacted requirements/entities/states/interfaces/risks and propose which tests should be created, updated or re-run.

See `docs/OPERATING_MODES.md`.

## Manual-first test authoring

Manual Test Cases are a first-class product of the engine, not merely a TMS formatting concern.

A generated or improved case should be able to include:

- stable internal ID;
- title and objective;
- origin/provenance;
- related requirement atoms/risks;
- environment/build/snapshot assumptions;
- actor/profile/permission requirements;
- preconditions;
- test data/parameters;
- ordered step-by-step actions;
- verified location/path when supported by evidence;
- Expected Result per validation step;
- Pass/Fail/Blocked semantics;
- cleanup/isolation;
- evidence expectations proportional to risk;
- Shared Step/parameter candidates;
- ambiguity/conflict/readiness state.

The output should be executable by another tester without relying on oral context. Generic framework conventions must never be used to invent a real screen, route, field, role, message or behavior.

See `docs/MANUAL_TEST_AUTHORING.md`.

## Trust model and anti-hallucination rules

The engine separates **authority**, **confidence** and **freshness**.

### Origin classes

| Origin | Meaning | Normative Pass/Fail? |
|---|---|---:|
| `CONTRACT` | approved product/business/regulatory/technical obligation | Yes |
| `IMPLEMENTATION` | behavior confirmed in code/schema/runtime/tests | Characterization/regression only unless separately approved |
| `ORGANIZATIONAL_POLICY` | explicit engineering/security/quality policy | Yes within declared scope |
| `RISK` | scenario derived from a credible failure mode | Only with a defensible invariant or explicit approval |
| `EXPLORATORY` | important hypothesis without sufficient oracle | No; charter/question only |

### Hard rules

- never invent a normative Expected Result;
- never treat implementation as approved contract without authority;
- never fabricate paths, roles, fields, states, endpoints, messages or side effects;
- never hide unreadable, blocked, partial or truncated evidence;
- never let a high confidence score replace source authority;
- never use RAG/GraphRAG/model summaries as terminal oracle evidence;
- never hard-code a real project's rules into the generic engine;
- never claim full analysis when required in-scope sources are incomplete;
- never silently convert risk/exploration into a formal requirement.

## Source completeness

Every run maintains a `SOURCE_LEDGER` and snapshot identity.

Relevant source states include:

- `STUDIED`;
- `PARTIALLY_STUDIED`;
- `NOT_STUDIED`;
- `BLOCKED`;
- `OUT_OF_SCOPE`;
- `SUPERSEDED`.

Read-integrity metadata is tracked independently. A run may continue with incomplete evidence, but it must downgrade its completeness claim and surface the exact limitation.

“Complete” means the required sources in the **explicit, discoverable/configured scope** were accounted for. It does not mean omniscience about artifacts the system could not possibly know existed.

## Existing history is preserved

In normal audit/sync behavior, the system must not automatically delete or erase:

- Test Cases;
- requirements/work items;
- test runs/results;
- comments;
- screenshots/attachments;
- bug/issue links;
- historical step results;
- requirement↔test traceability;
- execution evidence.

Duplicate/stale/obsolete findings become review proposals, not delete operations. Major semantic rewrites of already executed cases should prefer revision/replacement relationships where the TMS supports them.

See `docs/EXISTING_ASSET_AUDIT_POLICY.md`.

## Human approval and external writes

Analysis, auditing, scenario generation and manual Test Case generation are allowed without write permission to external systems.

Publication is a separate controlled action:

```text
Analyze
→ Generate / Audit
→ Validate
→ Preview / Diff
→ Human Review
→ Explicit Approval
→ Optional Publish / Update / Link
→ Read-back Verification
→ Persist External Mapping
```

No reasoning step implicitly grants CRUD authority.

Approval must be scoped to the exact proposal and snapshot. If the target changes between preview and write, the approval becomes stale and requires review again.

Destructive operations are disabled by default and remain outside normal generation/synchronization flow.

## Works without Azure DevOps, MCP or any TMS

The core engine and Agent Skill must be usable without Azure DevOps, MCP, Jira, TestRail or another external test-management connection.

Without a TMS connection, it can still:

- inventory local/repository evidence;
- build the Project Model;
- audit requirements and existing exported test assets;
- detect gaps/duplicates/conflicts;
- generate risks/scenarios;
- generate or improve manual step-by-step Test Cases;
- validate quality gates;
- export structured artifacts such as JSON/YAML/Markdown.

TMS integrations are optional adapters for live inventory, preview, publication and result ingestion. Azure DevOps is the first planned adapter, not a dependency of the core.

## Azure/TMS integration philosophy

The future Azure adapter supports modes such as:

- `AUDIT_ONLY`;
- `PREVIEW` / dry-run;
- `APPROVED_SYNC`.

It will use stable mappings/idempotency, re-read external state before mutation, preserve history and verify written artifacts after publication. Requirement/work-item types are mapped through project configuration rather than hard-coded assumptions.

See `docs/AZURE_DEVOPS_ADAPTER.md`.

## Quality engineering beyond documented requirements

The engine does not stop at `requirement has a linked TC`.

Depending on applicability, scenario analysis considers:

- happy and alternate paths;
- negative paths;
- equivalence classes and boundaries;
- state transitions and invalid transitions;
- roles/permissions;
- security;
- concurrency/race conditions;
- retry/idempotency/replay;
- failure/recovery;
- data integrity;
- time/date/timezone;
- configuration/environment;
- performance/measurement protocols;
- accessibility/operability;
- observability/auditability;
- optional human/physical-process risks for industrial/IoT workflows.

Risk-derived scenarios remain explicitly labeled as risk-derived. They do not become contractual requirements unless a governed human decision promotes them.

## Retrieval / RAG / GraphRAG

RAG and GraphRAG may be evaluated later as discovery aids for large corpora.

They never replace:

- deterministic source inventory;
- primary-source verification;
- source provenance;
- authority/conflict logic;
- project/snapshot isolation.

A retrieved or graph-derived claim must still resolve back to primary evidence before influencing a normative oracle.

## High-level architecture

```text
Scope / Run Manifest
        ↓
Source Inventory + Source Ledger
        ↓
Snapshot / hashes / integrity
        ↓
Safe parsers + AST/symbol analysis
        ↓
Claims + provenance + source authority
        ↓
Normalized Project Model
        ↓
Existing-test audit + atomic traceability
        ↓
Risk / Scenario Universe
        ↓
Optimization + duplicate classification
        ↓
Manual Test Model
        ↓
Quality Gates
        ↓
Human Review
        ↓
Optional Renderers / TMS Adapters
        ↓
Execution feedback / change impact
        ↓
Future automation renderers
```

## Roadmap

The project is deliberately incremental. The earlier fine-grained M0-M10 plan was consolidated without removing planned capabilities:

- **M0** — Foundations & Trust Model ✅
- **M1** — Source Ingestion & Project Model
- **M2** — Audit, Traceability & Risk Analysis ✅
- **M3** — Test Generation & Improvement ✓
- **M4** — Semantic QE & Production Agent Skill (active, local-first; D1 preview before H5)
- **M6** — Advanced Retrieval & Change Impact (after M4)
- **M5** — Automation & External Integrations (after M6)

M0-M3 form the standalone core product: local evidence can be ingested, modeled, audited and turned into reviewable manual Test Models without Azure DevOps, MCP or another TMS. Later milestones add optional integration, automation and advanced retrieval/change-impact capabilities.

Later milestones must not bypass trust foundations.

## Repository map

Start here:

- `AGENTS.md` — implementation contract for coding agents;
- `CLAUDE.md` — Claude implementation/audit instructions;
- `docs/INDEX.md` — documentation map;
- `docs/ENGINEERING_CONSTITUTION.md` — engineering rules;
- `docs/IMPLEMENTATION_SPEC.md` — implementation plan;
- `docs/M0_EVIDENCE.md`, `docs/M1_EVIDENCE.md` and `docs/M2_EVIDENCE.md` — milestone evidence;
- `docs/ROADMAP.md` — milestone sequence;
- `docs/STATUS.md` — documented vs implemented capability.

Trust/evidence:

- `docs/PROJECT_INPUT_CONTRACT.md`
- `docs/SOURCE_AUTHORITY.md`
- `docs/TRUST_MODEL.md`
- `docs/ORACLE_POLICY.md`
- `docs/PROJECT_MODEL.md`
- `docs/QUALITY_GATES.md`

Modes/manual/audit:

- `docs/OPERATING_MODES.md`
- `docs/MANUAL_TEST_AUTHORING.md`
- `docs/EXISTING_ASSET_AUDIT_POLICY.md`
- `docs/TEST_DESIGN_POLICY.md`

Risk/security/retrieval:

- `docs/RISK_MODEL.md`
- `docs/HUMAN_PHYSICAL_FACTORS.md`
- `docs/SECURITY_THREAT_MODEL.md`
- `docs/RETRIEVAL_STRATEGY.md`
- `docs/QUALITY_METRICS.md`
- `docs/STANDARDS_BASELINE.md`

Integration/skill:

- `docs/AGENT_SKILL_SPEC.md`
- `docs/AZURE_DEVOPS_ADAPTER.md`
- `skill/qe-engineering/SKILL.md`

Validation/research:

- `docs/EVAL_STRATEGY.md`
- `docs/AUDIT_GUIDE.md`
- `docs/BENCHMARKS.md`
- `docs/MARKET_LANDSCAPE.md`
- `docs/AI_IMPLEMENTATION_GUIDE.md`

## Current implementation status

**M0–M3 are implemented and validated. M4 Semantic QE & Production Agent Skill is active.**

The executable package includes M0/M1 trust and ingestion behavior plus deterministic audit and
traceability contracts, nominal versus atomic coverage, conservative existing-test/oracle/history
findings, clone revalidation, risk/scenario analysis, bounded scenario selection and local reports.
Arbitrary natural-language semantics are not claimed.

Install with `python -m pip install -r requirements-dev.lock`, followed by
`python -m pip install --no-deps --no-build-isolation -e .`. Run `qe --help` for validation,
inventory, ingestion, analysis, generation and rendering commands. See `docs/CLI.md` and the milestone evidence documents
for contracts, reproduction evidence and limitations.

M3 produces provenance-backed manual Test Model proposals and deterministic JSON/YAML/Markdown/
HTML reviews without external writes. M4.H1 provides the provider-neutral reasoning boundary and
M4.H2 provides non-normative, provenance-bound semantic candidate/cache contracts. M4.H3 adds
grounded multilingual normalization with PT-BR/mixed-language coverage and no authority promotion;
H4 adds evidence-validated non-authoritative relations. Real-document orchestration and production
skill packaging remain M4 work after D1 Technical Preview. External integrations/automation are M5,
after M6; whole-system audit, change impact and
advanced retrieval remain M6. Read `docs/STATUS.md` for the authoritative current state.

Build the current offline PT-BR Technical Preview from repository-local synthetic evidence:

```powershell
.\.venv\Scripts\python.exe -m tools.build_technical_preview
```

Then open `examples/technical-preview/output/test-plan.html`. This demonstrates validated local
rendering and H4 conflict visibility; it does not claim H5 arbitrary-document orchestration.
