# Test Design Policy

## Objective

Map the behavior/risk space comprehensively, then generate the smallest defensible executable set. Scenario coverage and test-case count are different metrics.

## Requirement/testability review before generation

Before creating cases, assess whether the input is testable. Techniques such as INVEST, 5W2H and Given/When/Then may help expose missing actor, value, dependency, trigger, data, timing, environment or observable outcome.

These are tools, not mandatory output formats. The final manual case must remain operationally executable by a human tester.

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
- exploratory charters;
- error guessing only as a labeled risk technique, never as hidden requirement inference.

## Scenario universe versus selected cases

The engine should preserve a traceable scenario universe, then record why scenarios were selected, merged, parameterized, deferred or covered by another layer. This avoids both unbounded combinatorial growth and false confidence from a tiny suite.

## Atomicity

A test may contain several sequential validations when they form one coherent objective and failure diagnosis remains clear. Independent oracles should be separate validation steps or separate cases. Avoid a single Expected Result that bundles unrelated conditions.

## Duplicate policy

Classify apparent duplicates as:

- `COMPLEMENTARY_LAYER`;
- `REGRESSION_INTENTIONAL`;
- `DATA_VARIANT`;
- `REDUNDANT`;
- `CONFLICTING`.

Do not count redundant wording variants as additional coverage.

## Manual step quality

Each step should identify, as needed:

- **where** the action occurs, using a verified path;
- **who** performs it/profile;
- **what** is prepared or selected;
- **action** to perform;
- **observable Expected Result**;
- relevant test-data properties;
- evidence required only when justified.

Do not include fixed record IDs/accounts/timestamps when parameters/data properties can express the requirement.

Given/When/Then may be used as an intermediate semantic form, but the manual renderer should translate it into operational actions when that is clearer for execution.

## Shared/reusable flow candidates

A repeated preparation flow may become a Shared Step candidate when it is stable, common and not the unique assertion under test. Reuse must not hide the behavior being validated.

## Measurement-sensitive cases

Timing, concurrency and performance cases require an explicit measurement/synchronization protocol. Define clocks, load, sample/repetition, environment and acceptance metric as appropriate. Do not rely on vague language such as “at the same time” when race-condition coverage matters.

## Pass, Fail, Blocked

- `PASS`: action executed and observed behavior satisfies the oracle.
- `FAIL`: action executed and observed behavior contradicts the oracle.
- `BLOCKED`: reliable execution cannot proceed because a prerequisite/path/environment/access dependency is unresolved; absence of execution evidence is not automatically Fail.

Adapters may map these semantics to TMS vocabulary.

## Evidence burden

A normal low-risk Pass should remain lightweight. Require stronger evidence for failures, blocked runs, critical controls, destructive/high-risk tests, regulated audit obligations or measurement-sensitive cases.
