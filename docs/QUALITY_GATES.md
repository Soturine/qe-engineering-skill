# Quality Gates

A test case is not trustworthy merely because it is valid JSON or well written. Publication requires layered gates.

## Gate A — Scope, identity and source completeness

- project/run/snapshot identity valid;
- required source containers inventoried;
- required sources accounted for;
- no silent retrieval/read/integrity failures;
- partial/truncated sources explicit;
- project isolation confirmed.

Failure: `BLOCKED_SOURCE`, run `PARTIAL`, or `INVALID`.

## Gate B — Provenance, authority and uncertainty

- every normative oracle resolves to primary evidence;
- source authority and confidence are separate;
- inference is labeled and cannot leak into contract;
- contradictions are resolved by legitimate precedence or explicitly block;
- stale/superseded sources are not silently preferred;
- derived confidence/authority does not exceed allowed evidence.

Failure: `REJECTED_UNSUPPORTED_ORACLE` or `AMBIGUOUS`.

## Gate C — Project-model integrity

- requirement atoms/actors/states/interfaces used by the case exist in the model;
- aliases are resolved or flagged;
- verified UI/API paths have provenance;
- source deletion/mutation invalidates dependents;
- model schema/version valid.

## Gate D — Test design

- objective is diagnostic and sufficiently atomic;
- independent oracles are separate validation steps/cases;
- happy/alternate/negative/boundary/state lenses considered as relevant;
- security/concurrency/resilience/time/data/accessibility packs considered by applicability;
- duplication is classified;
- risk rationale exists where applicable;
- scenario selection/omission rationale is traceable.

## Gate E — Manual executability

- preconditions can be prepared;
- actor/profile is known or parameterized;
- path is verified rather than guessed;
- test data can be created safely;
- action is reproducible;
- Expected Result is observable;
- Pass/Fail/Blocked semantics are clear;
- cleanup/isolation is defined where state persists;
- evidence burden is proportional to risk.

## Gate F — Safety and privacy

- authorization/privacy/security implications reviewed;
- destructive actions controlled;
- no secrets/sensitive raw evidence leaked;
- cross-project evidence leakage prevented;
- project content cannot override agent instructions;
- malicious input/export risks controlled.

## Gate G — Measurement protocol

When a case asserts timing, concurrency, throughput, durability or race behavior:

- measurement/synchronization method defined;
- clock/source/sample/load/environment specified as needed;
- a human stopwatch is not used as sole evidence for strict technical SLAs unless explicitly accepted.

## Gate H — TMS/renderer compatibility

Before adapter publication:

- field limits/workflow mappings validated;
- Shared Steps/parameters used appropriately;
- materially different workflows not collapsed incorrectly;
- links target valid work items;
- render round-trip does not alter oracle semantics.

## Gate I — Publication safety

- dry-run/preview/diff available for bulk changes;
- target scope revalidated;
- idempotency/mapping strategy prevents duplicates;
- explicit approval captured when required;
- external IDs/results logged.

## Gate J — Human review

Mandatory for:

- unresolved authority conflicts;
- inferred/risk-derived normative promotions;
- high/critical security/safety cases;
- destructive tests;
- bulk publication/update;
- first use of a new domain pack/adapter;
- material provider/model/prompt changes until eval confidence exists.

## Release gate for the skill itself

A release requires:

- unit/component/integration tests green as applicable;
- hard-invariant evals green;
- mutation/deletion/contradiction/prompt-injection/isolation evals at accepted thresholds;
- no known CRITICAL/HIGH provenance, isolation or unsafe-publication defects;
- schemas/docs synchronized;
- provider/prompt changes evaluated;
- release commit is last-known-green.
