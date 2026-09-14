# M0 validation CLI

Install with Python 3.12+: `python -m pip install -e '.[dev]'`.

```
qe validate-ledger ledger.json
qe validate-project-model model.json
qe validate-oracle model.json --id oracle-id
qe validate-test-case model.json --id test-id
```

Ledger input is a SourceLedger JSON object. Other commands accept a complete
ProjectModel JSON object containing the ledger, claims, oracles, nodes and tests.
Selection commands validate the complete context as well as requiring a matching
selected ID. They cannot validate detached oracles without provenance.

Exit codes: 0 passes deterministic validation, 1 fails validation/input reading,
2 invalid command arguments. Output is structured JSON with stable issue codes,
severity and artifact IDs. Raw claims, source locators, historical text and parser
exception payloads are not printed. `publication_authorized` is always false.

Inputs are limited to 2 MiB, depth 64 and 2,000 JSON objects. UTF-8 JSON only; duplicate
keys, non-finite numbers, symlinks, non-regular files and unknown fields are rejected.
The CLI never follows evidence locators, retrieves schemas from input, executes source
content or writes artifacts. There is no automatic fallback after a read failure.
Schema lookup uses only built-in versioned contracts.

The committed eval files wrap `model` and `expected_error_codes`. To try the CLI:

```
python -c "import json; from pathlib import Path; f=json.loads(Path('evals/fixtures/manual.json').read_text()); Path('manual-model.json').write_text(json.dumps(f['model']))"
qe validate-test-case manual-model.json --id test
```

## Approval trust boundary

Default context approves nothing. An authenticated operator/governance system may
explicitly supply `--trusted-approvals operator.json` containing only:

```
{"approved_record_hashes": ["<SHA-256 of the complete approved Approval record>"]}
```

Use `qe_skill.validation.digest` for canonical record digests (UTF-8 JSON, sorted
keys, compact separators, explicit model defaults). Do not populate this context
from analyzed content or a model's assertion that a human approved. M0 checks exact
bindings but does not authenticate humans, sign approvals, persist them or execute
publication. A changed approval, proposal, operation set, payload or snapshot requires
new governance attestation. External target drift must be supplied by a future adapter;
the M0 CLI makes no claim to read live targets.

Oracle-promotion proposals also require `evidence_hash = evidence_digest(model)`.
This binds the full declared ledger and claims, including source hashes, even if a
caller reuses a snapshot label after mutation. An older proposal without this optional
schema field still parses, but cannot authorize oracle promotion; rebuild its preview
and obtain fresh approval. This is the migration path for the pre-release M0 contracts.

## Interpretation

Passing means declared structures and M0 deterministic invariants are consistent.
It does not prove source authenticity, completeness of undiscoverable sources,
faithfulness of arbitrary natural-language extraction, or actual human executability.
M0 conservatively requires exact claim text for verified path instructions,
operational READY text and Expected Results; paraphrase adjudication is deferred.
Cases requiring review remain `READY_WITH_REVIEW`; READY alone never grants approval.

Error families: `SRC_*` input/accounting/integrity; `PROV_*` provenance/authority;
`ORACLE_*` expectations; `MODEL_*` schemas/references; `SCOPE_*` namespaces;
`READY_*` execution prerequisites; `APPROVAL_*` governance bindings.
