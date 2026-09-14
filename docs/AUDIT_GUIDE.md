# Repository and Skill Audit Guide

This guide is for an independent reviewer, coding/review agent, another Agent Skill or a human engineer.

## Audit objective

Determine whether the repository deserves trust—not whether its documentation sounds convincing.

## Phase 1 — Inventory

List root policies, normative docs, schemas, code modules, adapters/providers, tests, evals, skill files and CI/release configuration. Identify missing referenced artifacts, dead links and documentation that claims unimplemented enforcement.

## Phase 2 — Policy-to-code traceability

For every non-negotiable claim in `AGENTS.md`, `ENGINEERING_CONSTITUTION`, `TRUST_MODEL`, `ORACLE_POLICY`, `SOURCE_AUTHORITY` and `QUALITY_GATES`, locate the implementation control/test/eval or mark it documentation-only/unimplemented.

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
- UI/API path absent from evidence;
- duplicate cases with different wording;
- low-confidence extraction asserted as certain;
- stale/poisoned cache;
- hash/source-ID mismatch;
- symlink/path traversal;
- malicious archive/oversized input;
- secret-bearing source;
- spreadsheet/export injection;
- false approval metadata;
- publication retry/idempotency;
- schema migration;
- provider/model/prompt drift;
- context-window pressure/large corpus.

## Phase 4 — Generic/domain leakage

Inspect code and evals for hard-coded rules belonging to a particular real project. Mutation/deletion fixtures must prove the engine follows current evidence rather than memorized examples.

## Phase 5 — Provider parity

If multiple providers are supported, compare semantic extraction properties and deterministic gate outcomes. Provider disagreement must not weaken hard invariants.

## Phase 6 — TMS/publication safety

Where write adapters exist, verify dry-run/diff, target scope, explicit approval, idempotency, safe retries, audit records and absence of invented target fields.

## Phase 7 — Self-audit

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
