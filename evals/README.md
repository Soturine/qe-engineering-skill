# Evaluation Fixtures

Status: **M1 deterministic synthetic evals implemented**

Run `python -m pytest evals`. Rebuild committed JSON using
`python -m evals.build_fixtures`; tests reject drift. The eleven fixtures cover
greenfield without TCs, executable manual model, vague/duplicate/stale brownfield
assets, clone/reuse with conflicting historical oracles, rejected foreign oracle,
blocked/partial evidence, rejected false completeness, unsupported oracle,
ambiguity/risk-only scenarios, inert prompt injection and regression baseline shape.

Each fixture declares expected error codes; valid partial evidence is accepted with
visible warnings, while normative output depending on unavailable evidence fails.
Validation must not mutate history. Mode dispatch, semantic audit, external write
execution and live provider parity are deferred; mode fixtures test contract shapes.

`test_m1_ingestion.py` adds live synthetic temporary-project evals for representative
provenance-backed normalization, inert prompt injection, visible parser failure and blocked
remote references. These evals use no model, network service or TMS.

Committed fixtures must be synthetic and generic. Do not copy confidential requirements, production data, real customer repositories or proprietary artifacts into this directory.

Planned fixture families:

- `web/`
- `api/`
- `mobile/`
- `data/`
- `async-concurrency/`
- `industrial/`
- `adversarial/`

Each fixture should document planted facts, planted ambiguity/conflicts, expected hard-gate outcomes and mutations/deletions. Prefer invariant/property expectations over exact generated wording.

See `docs/EVAL_STRATEGY.md`.
