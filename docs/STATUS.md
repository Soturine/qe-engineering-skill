# Implementation Status

## Current stage

**M1 - Source Ingestion & Project Model: implemented and locally validated.**

M0 trust contracts remain binding. M1 adds deterministic local evidence accounting, bounded
parsing, provenance-bearing extraction and conservative Project Model population. See
`M1_EVIDENCE.md` for supported types, tests, boundaries and exit criteria. The current commit
must remain green on Linux and Windows CI before release; no tag/release exists.

## Implemented

- Python 3.12+ typed modular-monolith package; no model/TMS runtime dependency.
- M0 reproducible schemas, strict domain contracts and trust/readiness validators.
- Ledger completeness, authority, provenance, namespace, mutation and approval gates.
- Deterministic local inventory with stable relative paths, SHA-256 and explicit states.
- Include/exclude scope, generated-directory defaults, size/count/depth limits and confined
  file-symlink behavior.
- Bounded UTF-8 Markdown/plain-text, JSON, safe YAML, OpenAPI and Python AST parsers.
- Typed extraction/span/result contracts with project/snapshot/source-hash bindings.
- Conservative builder for explicit `qe_model` records and raw OpenAPI structural declarations.
- Requirements/criteria, entities/fields/constraints/relationships, actors/roles/groups/
  permissions, states/transitions/channels/actions/events, interfaces/integrations, invariants,
  ambiguities/conflicts/aliases, verified paths and historical test/result evidence nodes.
- Local `inventory` and `ingest` CLI commands with structured JSON artifacts and no network,
  model, TMS or publication dependency.
- Synthetic unit/integration/adversarial evals and Linux/Windows CI.

## M1 limitations

- Arbitrary natural-language documents are structurally parsed but not promoted into domain
  semantics. Semantic normalization requires the explicit generic `qe_model` structure.
- Local and remote OpenAPI references are recorded but not resolved. Remote references are
  never fetched and make the affected parse partial.
- PDF/DOCX, archives, binaries and code languages other than Python have no semantic parser.
- Parsing is byte/depth/record bounded in-process; a separate OS sandbox and hard wall-clock/
  memory limiter are not implemented.
- Authority/lifecycle classification is operator configuration. M1 does not authenticate source
  authorship, signatures, human reviewers or mutable remote systems.
- Exact approval bindings are validated, but authentication, signing, durable storage and
  external enforcement remain deferred.
- Existing tests/results are evidence nodes only; no audit or quality classification is inferred.
- Conflict preservation is implemented; M1 does not choose authority or synthesize resolutions.

## Deferred by milestone

- **M2 - Audit, Traceability & Risk Analysis:** existing-test audit, atomic coverage, duplicate/
  conflict/stale classification, risk/scenario generation and coverage optimization.
- **M3 - Test Generation & Improvement:** production manual generator/rewriter, greenfield plans,
  missing-case generation and step-by-step rewrite proposals.
- **M4 - Integrations & Production Agent Skill:** Azure/MCP/TMS adapters, preview/sync,
  target-drift/read-back/idempotency execution and production Agent Skill packaging.
- **M5 - Automation & Execution Assistance:** automation renderers and optional bounded
  execution/evidence-capture assistance.
- **M6 - Advanced Retrieval & Change Impact:** RAG/GraphRAG evaluation, richer code dependency
  graphs, PR/diff impact analysis and regression selection.

## Safety interpretation

Inventory/parsing executes no analyzed content and preserves its inputs. Destructive operations
are absent. Historical identity cannot resolve as destination evidence. Passing M1 validation
does not prove source authenticity, arbitrary semantics, undiscoverable-source completeness,
human executability or publication authority. Unknown, partial and conflicting evidence remains
visible rather than being replaced with an inferred fact.
