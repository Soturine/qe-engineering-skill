# Schemas

Status: **M0 scaffold**

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
