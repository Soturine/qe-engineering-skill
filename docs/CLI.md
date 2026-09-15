# Local validation and M1 ingestion CLI

Install with Python 3.12+. In a repository checkout, use the environment-local interpreter:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.lock
.\.venv\Scripts\python.exe -m pip install --no-deps --no-build-isolation -e .
```

## M1 local source commands

Inventory requires an explicit directory, project/snapshot namespace and reproducible UTC
collection timestamp:

```powershell
.\.venv\Scripts\python.exe -m qe_skill.cli inventory .\synthetic-project `
  --project-id synthetic --snapshot-id snapshot-1 `
  --collected-at 2026-01-01T00:00:00Z --output-dir .\output
```

Run the complete inventory, parse, extraction, Project Model and M0-validation pipeline:

```powershell
.\.venv\Scripts\python.exe -m qe_skill.cli ingest .\synthetic-project `
  --project-id synthetic --snapshot-id snapshot-1 `
  --collected-at 2026-01-01T00:00:00Z `
  --authority-class GUIDANCE --lifecycle active --output-dir .\output
```

Repeat `--include` or `--exclude` for explicit glob scope. `--max-files`, `--max-bytes` and
`--max-depth` set hard bounds. Defaults are 10,000 files, 2 MiB per file and depth 32. Common
generated/runtime directories including `.git`, `.venv`, caches, build, `dist`, `node_modules`
and `output` are not traversed. File symlinks are followed only when their target remains inside
the configured root; directory symlinks are never followed.

With `--output-dir`, inventory writes `source-inventory.json`, `run-manifest.json` and
`source-ledger.json`. Ingestion additionally writes `extraction.json`, `project-model.json` and
`ingestion-report.json`.

The console contains a compact structured summary, not raw source. Exit code 0 means the local
scope completed; partial/invalid ingestion returns 1 and invalid arguments return 2. Local
artifact writing is the only side effect. No network, external CRUD or publication exists.

## M2 local analysis

Analyze a versioned Project Model produced by ingestion or another validated local source:

```powershell
.\.venv\Scripts\python.exe -m qe_skill.cli analyze .\output\project-model.json `
  --max-scenarios 100 --max-pairwise-combinations 24 `
  --output-dir .\audit-output
```

The command validates the Project Model, rejects M6 regression mode, and writes typed
`traceability.json`, `coverage-report.json`, `audit-findings.json`, `risk-analysis.json`,
`scenario-universe.json`, `proposals.json`, `m2-analysis-report.json` and `audit-report.md`.
Scenario limits are positive bounded integers. Output ordering and IDs are stable for identical
input and configuration.

Analysis is read-only. Historical tests/results remain unchanged, proposals contain no external
operations, and risk scenarios without a defensible oracle remain exploratory. The report marks
incomplete evidence and unreliable coverage denominators instead of claiming full certainty. The
command does not create final manual Test Cases; that remains M3.

Authority defaults to `GUIDANCE`; claims therefore remain exploratory unless the operator
classifies the source. Contract/policy authority requires an approved lifecycle to pass M0
provenance validation. Project content cannot select authority or approve itself.

## Supported semantic input

Markdown/text yield document structure only. Python yields AST symbols/imports/decorators only.
These structures are not guessed to be requirements, routes, roles or rules.

Raw OpenAPI JSON/YAML yields declared operations, parameters, response statuses/schema refs,
security, component schemas and fields. It does not create business requirements or fetch refs.

Generic deterministic semantic normalization uses an explicit top-level `qe_model` object in
JSON or YAML. Supported collections include requirements/criteria, entities/fields/constraints/
relationships, actors/roles/groups/mappings/permissions, states/transitions/channels/actions/
events, interfaces/integrations, invariants, decision rules, ambiguities/conflicts/aliases,
verified paths and existing test/result evidence. M2 audit fields on existing tests and structured
constraint bounds/partitions are accepted only when explicitly declared. Each record needs a
globally unique explicit `id`; relationships use explicit `*_id`/`*_ids` fields. Malformed records
are reported rather than guessed.

## M0 validation commands

```text
qe validate-ledger ledger.json
qe validate-project-model model.json
qe validate-oracle model.json --id oracle-id
qe validate-test-case model.json --id test-id
```

Ledger input is a SourceLedger JSON object. Other commands accept a complete ProjectModel JSON
object. Selection commands validate the complete context as well as requiring a matching ID.
Inputs are limited to 2 MiB, depth 64 and 2,000 JSON objects; duplicate keys, non-finite values,
symlink inputs and unknown fields are rejected. Output never authorizes publication.

## Approval trust boundary

Default context approves nothing. An authenticated operator/governance system may supply
`--trusted-approvals operator.json` containing only:

```json
{"approved_record_hashes": ["<SHA-256 of the complete approved Approval record>"]}
```

Use `qe_skill.validation.digest` for canonical record digests. Do not populate trusted context
from analyzed content or a model assertion. M0 checks exact bindings but does not authenticate
humans, persist approvals or publish. Oracle promotion also requires
`evidence_hash = evidence_digest(model)` so evidence mutation invalidates approval.

## Interpretation

Passing validates implemented deterministic contracts for the declared scope. It does not prove
authenticity, undiscoverable-source completeness, arbitrary natural-language semantics, human
executability or publication safety. Error families remain `SRC_*`, `PROV_*`, `ORACLE_*`,
`MODEL_*`, `SCOPE_*`, `READY_*` and `APPROVAL_*`; M1 adds `BUILD_*` limitations.
