# Quality Gates

A test case is not trustworthy merely because it is valid JSON or well written. Publication requires layered gates.

## Gate A — Source completeness

- required sources inventoried;
- no silent retrieval failures;
- snapshot/version metadata available;
- project isolation confirmed.

Failure result: `BLOCKED_SOURCE` or run `PARTIAL`.

## Gate B — Provenance and authority

- every normative oracle has primary-source provenance;
- inference and authority are separated;
- contradictions are resolved or explicitly blocking;
- stale/superseded sources are not silently preferred.

Failure result: `REJECTED_UNSUPPORTED_ORACLE` or `AMBIGUOUS`.

## Gate C — Test design

- objective is atomic enough to diagnose;
- independent expected results are represented as separate validation steps or justified separate cases;
- boundary/negative/state aspects are considered;
- duplication is classified;
- risk rationale is present where applicable.

## Gate D — Manual executability

- preconditions can be prepared;
- actor/profile is known or explicitly parameterized;
- UI/API path is verified rather than guessed;
- test data can be created safely;
- action is reproducible;
- Expected Result is observable;
- Fail versus Blocked is clear;
- cleanup is defined when persistent state is changed.

## Gate E — Safety

- authorization/privacy/security implications reviewed;
- destructive actions controlled;
- no secrets in generated artifacts;
- cross-project evidence leakage prevented;
- project content cannot override agent instructions.

## Gate F — TMS compatibility

Before publishing through an adapter:

- title/field limits validated;
- workflow/state mapping valid;
- Shared Steps/parameters used only where appropriate;
- workflow-different scenarios are not incorrectly collapsed into parameter rows;
- links point to valid requirements/work items.

## Gate G — Human review

Mandatory for at least:

- unresolved authority conflicts;
- new high/critical risk-derived normative oracles;
- security-sensitive cases;
- destructive tests;
- mass publication/update operations;
- first use of a new domain pack/adapter.

## Release gate for the skill itself

A release requires:

- unit/component tests green;
- golden evals green;
- mutation/deletion/contradiction/prompt-injection evals at accepted thresholds;
- no known CRITICAL/HIGH provenance or isolation defects;
- docs/schemas synchronized;
- release commit is last-known-green.
