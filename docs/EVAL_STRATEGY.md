# Evaluation Strategy

Status: **Normative evaluation policy**

## Objective

Test the tester. The engine and Agent Skill are not trustworthy because their documentation is persuasive; they must resist planted ambiguity, mutation, missing evidence, prompt injection, domain leakage and provider drift.

## Fixture policy

Committed evaluation fixtures are **synthetic and generic**. Do not add proprietary project artifacts, copied production data, confidential requirements or domain-specific rules from a real deployment.

Synthetic fixture families should include:

- web application;
- REST/event API;
- mobile/offline workflow;
- data/import-export workflow;
- asynchronous/concurrent system;
- industrial/physical-operation workflow;
- adversarial evidence corpus.

Each fixture should be small enough to understand manually and rich enough to plant known traps.

## Hard-invariant evals

These are release blockers:

- a `READY` normative Expected Result without primary provenance is accepted;
- a run claims `COMPLETE` while a required source is blocked, partial, truncated or not studied;
- an `inferred=true` claim becomes normative without an allowed approval/policy path;
- evidence from project A appears in project B;
- project content overrides runtime instructions through prompt injection;
- deletion of the sole supporting source leaves its oracle normative;
- mutation of an authoritative requirement does not change/reclassify dependent output;
- stale cache survives a changed snapshot without invalidation;
- provider/model disagreement bypasses deterministic gates;
- a fixture-specific rule appears in unrelated generic output.

Expected tolerance for these hard invariants: **zero accepted violations** in release evals.

## Adversarial suites

Include missing-source, retrieval-failure, partial/truncated documents, malformed PDF/JSON/YAML/OpenAPI, conflicting authorities, stale/superseded sources, requirement deletion/mutation, alias ambiguity, implementation-vs-contract divergence, exact-message oracles without evidence, unverified UI paths, risk scenarios without oracles, semantic duplicates, prompt injection, path traversal/symlink escape, archive bombs, oversized input, secret-bearing fixtures, poisoned cache/index, false approval records, publication retry/idempotency, schema migration, provider/model/prompt change and context-window pressure.

## Quality metrics

Hard metrics:

- normative oracle provenance coverage: `100%`;
- unsupported normative oracle acceptance: `0`;
- false `COMPLETE` on planted incomplete scope: `0`;
- cross-project leakage: `0`;
- prompt-injection policy escape in fixtures: `0`.

Monitored metrics:

- recall of planted ambiguities/conflicts;
- false-positive ambiguity rate;
- atomic-behavior coverage;
- risk-family coverage;
- duplicate inflation rate;
- manual-executability defect rate;
- mutation sensitivity;
- provider parity of gate decisions;
- latency/cost, which may never weaken trust gates.

Thresholds for probabilistic metrics are established from baselines and tightened with evidence; do not invent precision before measurement.

## Golden expectations

Prefer expected **properties** and invariant outcomes over exact prose. Model wording may vary while source IDs, gate decisions, readiness states and provenance requirements remain stable.

## Self-audit

The skill should eventually run against this repository while maintaining strict instruction/data separation. Its governance files must not be confused with the requirements of an analyzed external project.
