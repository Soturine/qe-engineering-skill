# Quality Metrics

Status: **Measurement policy**

## Principle

More test cases are not automatically better testing. Metrics should reward evidence quality, behavioral/risk coverage and defect-detection value—not output volume.

## Hard trust metrics

Release-blocking targets:

- normative Expected Results with valid provenance: `100%`;
- accepted unsupported normative oracles: `0`;
- false `COMPLETE` in planted incomplete-source fixtures: `0`;
- cross-project evidence leakage in evals: `0`;
- prompt-injection policy escapes in evals: `0`.

## Coverage metrics

Track separately:

- requirement-ID nominal coverage;
- atomic criterion coverage;
- state-transition coverage;
- decision-table rule coverage;
- permission/role coverage;
- negative/boundary coverage;
- risk-family coverage;
- integration/interface coverage;
- critical-path E2E coverage.

Never collapse all of these into one misleading percentage.

## Test quality metrics

- duplicate/redundancy ratio;
- grouped-independent-oracle rate;
- manual executability defect rate;
- blocked-due-to-missing-context rate;
- ambiguity detection recall on synthetic fixtures;
- false-positive ambiguity rate;
- mutation sensitivity;
- stale-source/conflict detection rate;
- cleanup/test-data reproducibility rate.

## Model-assisted metrics

- provider parity on deterministic gate outcomes;
- unsupported-claim rate;
- provenance-link accuracy;
- extraction precision/recall on labeled fixtures;
- drift after provider/model/prompt change.

## Operational metrics

Latency, cost and token usage matter, but are subordinate to trust gates. Optimizing cost must never convert a required source into an unreported omission or skip primary-source verification.
