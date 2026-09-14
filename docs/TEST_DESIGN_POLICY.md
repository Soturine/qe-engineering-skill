# Test Design Policy

## Objective

Map the behavior/risk space comprehensively, then generate the smallest defensible executable set. Scenario coverage and test-case count are different metrics.

## Required lenses

For each relevant capability consider:

- happy path;
- alternate paths;
- negative/invalid inputs;
- boundaries;
- state transitions and invalid transitions;
- actor/profile/authorization;
- cross-resource/tenant access;
- concurrency/races;
- retries/idempotency/replay;
- network/partial failure/recovery;
- data integrity/consistency;
- time/date/timezone/expiry;
- performance/capacity where specified or risk-justified;
- accessibility/operability;
- observability/audit trail;
- configuration/environment differences;
- hardware/physical/human factors when applicable.

## Techniques

Use the technique that fits the structure:

- equivalence partitioning;
- boundary-value analysis;
- decision tables;
- state-transition testing;
- pairwise/combinatorial selection;
- cause-effect modeling;
- risk-based prioritization;
- error guessing only as a labeled risk technique, never as hidden requirement inference.

## Atomicity

A test may contain several sequential validations when they form one coherent objective and failure diagnosis remains clear. Independent oracles should be separate validation steps or separate cases. Avoid a single Expected Result that bundles unrelated conditions.

## Duplicate policy

Classify apparent duplicates as:

- `COMPLEMENTARY_LAYER` (e.g., isolated functional + E2E);
- `REGRESSION_INTENTIONAL`;
- `DATA_VARIANT`;
- `REDUNDANT`;
- `CONFLICTING`.

Do not count redundant wording variants as additional coverage.

## Manual step quality

Each step should identify where/action/observable result as needed without unnecessary evidence burden. Do not include fixed IDs/EPCs/accounts when parameters can express the required data properties.

## Pass, Fail, Blocked

- `PASS`: action executed and observed behavior satisfies oracle.
- `FAIL`: action executed and observed behavior contradicts oracle.
- `BLOCKED`: reliable execution cannot proceed because a prerequisite/path/environment/access dependency is unresolved; absence of execution evidence is not automatically Fail.

Adapters may map these semantics to the TMS vocabulary.
