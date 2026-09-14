# Schemas

Status: **M0 version 1.0 contracts implemented; policy validators pending**

Schemas are in `v1/`. Reproduce with `python -m qe_skill.schemas`.
Tests check Draft 2020-12 validity and byte-for-byte agreement with typed contracts.
See `docs/adr/0001-versioned-trust-contracts.md` for authority and evolution rules.

This directory will contain versioned machine-verifiable contracts. Do not treat planned schemas as implemented until the files and validators exist.

Planned initial schemas:

- `run-manifest.schema.json`
- `source-ledger.schema.json`
- `claim-provenance.schema.json`
- `oracle.schema.json`
- `risk.schema.json`
- `project-model.schema.json`
- `test-case.schema.json`
- `approval.schema.json`

JSON Schema handles shape/basic constraints. Cross-artifact invariants (for example, `COMPLETE` versus source states or normative oracle provenance) must also be enforced in domain validators and evals.
