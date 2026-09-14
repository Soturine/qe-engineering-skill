# Repository and Skill Audit Guide

This guide is for an independent reviewer, coding/review agent, another Agent Skill or a human engineer.

## Audit objective

Determine whether the repository deserves trust—not whether its documentation sounds convincing.

## Phase 1 — Inventory

List root policies, normative docs, schemas, code modules, adapters/providers, tests, evals, skill files and CI/release configuration. Identify missing referenced artifacts, dead links and documentation that claims unimplemented enforcement.

## Phase 2 — Policy-to-code traceability

For every non-negotiable claim in `AGENTS.md`, `ENGINEERING_CONSTITUTION`, `TRUST_MODEL`, `ORACLE_POLICY`, `SOURCE_AUTHORITY`, `OPERATING_MODES`, `EXISTING_ASSET_AUDIT_POLICY`, `MANUAL_TEST_AUTHORING` and `QUALITY_GATES`, locate the implementation control/test/eval or mark it documentation-only/unimplemented.

Documentation volume is not evidence of enforcement.

## Phase 3 — Adversarial fixtures

Attempt at least:

- required source missing;
- connector/read failure;
- partial/truncated source;
- malformed structured input;
- contradictory authorities;
- implementation contradicts contract;
- source deleted after prior run;
- requirement value mutated;
- superseded source with newer timestamp;
- prompt injection inside source;
- two projects with identical names/entities;
- risk scenario lacking oracle;
- UI/API/manual path absent from evidence;
- duplicate cases with different wording;
- low-confidence extraction asserted as certain;
- stale/poisoned cache;
- hash/source-ID mismatch;
- symlink/path traversal;
- malicious archive/oversized input;
- secret-bearing source;
- spreadsheet/export injection;
- false approval metadata;
- stale approval after target drift;
- publication retry/idempotency;
- attempted cross-project/snapshot write;
- attempted destructive update of historical execution evidence;
- brownfield rewrite that mutates an executed TC without review;
- clone/reuse case that carries an old oracle without destination evidence;
- operation with no TMS/MCP connector available;
- schema migration;
- provider/model/prompt drift;
- context-window pressure/large corpus.

## Phase 4 — Operating-mode behavior

Validate independently:

### Greenfield

Given project evidence and no meaningful Test Plan, confirm the engine can build a Project Model and propose a complete manual Test Model to the level justified by evidence without requiring a TMS connection.

### Brownfield

Given existing requirements/tests/executions, confirm the engine audits before proposing changes, preserves history, finds atomic coverage gaps and can propose improved step-by-step cases without applying them automatically.

### Clone/reuse

Given imported tests plus destination evidence, confirm old paths/oracles/roles/states are revalidated and not silently treated as destination truth.

### Incremental/regression

When implemented, confirm a baseline plus change set produces impact/re-run proposals without weakening source/provenance rules.

## Phase 5 — Manual authoring quality

Verify that generated/rewrite proposals are operationally executable:

- preconditions are preparable;
- actor/profile is known or parameterized;
- path is evidenced or explicitly unresolved;
- test data is reproducible;
- actions are unambiguous;
- Expected Results are observable and traceable;
- independent validations are diagnosable;
- cleanup/isolation is defined where needed;
- evidence burden is proportional to risk.

## Phase 6 — Generic/domain leakage

Inspect code and evals for hard-coded rules belonging to a particular real project. Mutation/deletion fixtures must prove the engine follows current evidence rather than memorized examples.

## Phase 7 — Provider parity

If multiple providers are supported, compare semantic extraction properties and deterministic gate outcomes. Provider disagreement must not weaken hard invariants.

## Phase 8 — TMS/publication safety

Where write adapters exist, verify:

- connector is optional for core audit/generation;
- read/audit-only operation works;
- dry-run/diff;
- target scope;
- explicit human approval;
- approval bound to exact proposal/snapshot;
- stale-target detection;
- idempotency;
- safe retries;
- read-back verification;
- audit records;
- historical comments/screenshots/results are preserved;
- destructive delete/unlink/history rewrite is disabled by default;
- no invented target fields/process mappings.

## Phase 9 — Self-audit

Run the skill against this repository. Confirm instruction/data separation and no recursive agent-on-agent failure.

## Finding format

Each finding includes:

- ID;
- severity `CRITICAL|HIGH|MEDIUM|LOW|INFO`;
- evidence (file/symbol/line or reproducible command);
- violated invariant/policy;
- impact;
- reproduction;
- recommended fix;
- confidence.

## Terminal recommendation

- `SHIP`
- `FIX BEFORE MERGE`
- `BLOCK`

Do not manufacture findings, but do not praise without adversarial testing.
