# Schemas

Status: **M0 version 1.0 contracts and policy validators implemented**

Schemas are in `v1/`. Reproduce with `python -m qe_skill.schemas`.
Tests check Draft 2020-12 validity and byte-for-byte agreement with typed contracts.
See `docs/adr/0001-versioned-trust-contracts.md` for authority and evolution rules.

Implemented schemas in `v1/`:

- `run-manifest.schema.json`
- `source-ledger.schema.json`
- `claim-provenance.schema.json`
- `oracle.schema.json`
- `risk.schema.json`
- `project-model.schema.json`
- `test-case.schema.json`
- `approval.schema.json`
- `proposal.schema.json`
- `test-model.schema.json`
- `source-inventory.schema.json`
- `source-extraction.schema.json`
- `project-build.schema.json`
- `ingestion-report.schema.json`

JSON Schema handles shape/basic constraints. Cross-artifact invariants are implemented
in `qe_skill.validation` and `qe_skill.integrity`, with negative tests and evals.
