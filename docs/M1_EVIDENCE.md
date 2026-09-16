# M1 implementation evidence

Status: **implemented and validated for M1**. No release/tag created. Quality run
[`34930197646`](https://github.com/Soturine/qe-engineering-skill/actions/runs/34930197646)
passed on Linux and Windows, including installed-wheel verification.

## Implemented pipeline

```text
explicit local root and include/exclude scope
  -> deterministic inventory and SHA-256 identity
  -> M0 Run Manifest and Source Ledger
  -> bounded non-executing parsers
  -> typed extraction records with spans/locators
  -> conservative Project Model builder
  -> existing M0 integrity/trust validation
```

All artifacts retain `project_id`, `snapshot_id`, source ID and source hash. Parse/build failure,
unsupported content, limits, symlink escape and mutation remain visible. Discovery alone is
`NOT_STUDIED/UNVERIFIED`; only a successful complete parser changes a source to
`STUDIED/COMPLETE`. Partial/failed required evidence prevents a complete ingestion result.

## Supported source types

| Type | Deterministic support | Semantic boundary |
|---|---|---|
| Markdown | headings/levels/explicit IDs, paragraphs, list items, code-fence boundaries, line spans | no automatic requirement classification |
| Plain text | paragraphs and list items with line spans | no automatic domain classification |
| JSON | duplicate-key rejection, finite values, bounded data and JSON-pointer locations | explicit `qe_model` only for generic domain semantics |
| YAML | `SafeLoader`, duplicate-key detection, bounded data; arbitrary Python tags rejected | implicit timestamps must be quoted; explicit `qe_model` only |
| OpenAPI JSON/YAML | paths/methods, operations, parameters, request/response schema refs, statuses, security, schemas/properties/required fields | structural API evidence, not business requirements |
| Python | standard-library AST modules/classes/functions/async functions/imports/decorators/signatures/spans | never imported; decorators are syntax, not verified routes |

M1 originally left archives, binaries, PDF/DOCX and other code languages unsupported. M4.H5 now
adds bounded, inert extraction for HTML visible text, DOCX OpenXML paragraphs and text-bearing PDF
pages. DOCX is treated as a narrowly scoped document container, not as a general archive: member
paths, count and expanded size are bounded, macros/relationships are never executed or fetched.
Scanned/image-only PDF remains explicitly partial because OCR is not attempted. Other archives,
binaries and code languages remain unsupported.

## Project Model capability

Raw OpenAPI can populate evidence-backed API interfaces/channels/actions, parameter constraints,
response/security claims and technical entities/fields. The explicit generic `qe_model`
structure can populate requirements/atomic criteria, entities/fields/constraints/relationships,
actors/roles/groups/mappings/permissions, states/transitions/channels/actions/events,
interfaces/integrations, invariants, ambiguities/conflicts/aliases, verified paths and historical
test/result evidence.

Every created semantic node has claim/source provenance. Explicit duplicate IDs with different
content produce an unresolved conflict. Heuristic/inferred or foreign-project extraction records
are rejected. M1 creates no normative oracles and no generated tests.

## Security and trust boundaries

- local filesystem/repository input only;
- no shell, import, macro, template, browser, plugin or analyzed-content execution;
- no remote `$ref` fetch; local refs are recorded but not resolved;
- root confinement and explicit internal-file/external/directory symlink behavior;
- byte, file-count, structured-record, nesting and traversal-depth bounds;
- UTF-8 decoding only and concise errors without parser payload/source dumps;
- no network/model/Azure/MCP/TMS dependency and no external write authority;
- local output only when the operator supplies `--output-dir`;
- project/snapshot/source-hash validation before semantic normalization.

PyYAML 6.0.3 is the original M1 runtime dependency; M4.H5 additionally pins pypdf 6.19.0 for
bounded local PDF text extraction. `types-PyYAML` is pinned for strict typing. All are in the
complete development lock and supply-chain gates. The published PyPI advisory
audit is point-in-time evidence, not a guarantee that no vulnerability exists.

## Automated evidence

The final local suite contains 119 unit/component/integration tests and 26 evals. Coverage includes
stable ordering/hashes, mutation/deletion, empty/nested/Unicode roots, generated-directory ignores,
include/exclude rules, unreadable and oversized files, file-count/depth limits, internal/external
symlinks, malformed/duplicate/deep/large JSON/YAML, safe-tag rejection, inert prompt injection,
OpenAPI refs/cycles/security/schema facts, Python syntax/non-execution, provenance, inference and
cross-project rejection, conflicts, determinism and the complete CLI artifact pipeline.

Reproduce with the repository-local environment:

```powershell
$py = ".\.venv\Scripts\python.exe"
& $py -m pip check
& $py -m ruff check .
& $py -m ruff format --check .
& $py -m mypy
& $py -m pytest tests --basetemp .\.pytest-tmp -p no:cacheprovider
& $py -m pytest evals --basetemp .\.pytest-tmp-evals -p no:cacheprovider
& $py -m tools.audit_dependencies
```

The repo-local pytest base directory is only a Windows workaround for stale user-temp ACLs and is
removed after the run. The symlink test may skip where the local account cannot create symlinks;
the same behavior is exercised on a symlink-capable CI runner.

## Known limitations

- Natural-language semantic extraction is deliberately not implemented; unclassified evidence
  remains structural source material rather than guessed Project Model truth.
- OpenAPI refs are recorded but not resolved. Remote refs make the parse partial; local cycles are
  inert because no resolver runs.
- YAML implicit timestamp objects are rejected unless quoted, preserving JSON-compatible output.
- Parsers run in-process with byte/depth/record limits; an OS process sandbox and hard CPU/memory
  quota are not implemented.
- Inventory records filesystem size and content hash but does not authenticate authorship/signatures
  or capture Git commit identity automatically.
- Authority/lifecycle configuration is global for the current CLI run; per-source policy mapping is
  a future refinement.
- Existing tests/results are evidence nodes only. Audit, coverage, risk/scenario analysis and
  improvement proposals are M2.
- Manual test generation is M3; TMS/Azure/MCP writes and automation are M5 after M6; RAG/GraphRAG and
  change impact are M6.

M1 is not a claim that arbitrary projects are fully understood. It is a deterministic,
provenance-preserving foundation that reports unsupported or unresolved meaning instead of
inventing it.
