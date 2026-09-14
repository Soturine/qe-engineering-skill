# Evaluation Fixtures

Status: **M0 scaffold**

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
