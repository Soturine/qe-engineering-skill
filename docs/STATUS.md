# Implementation Status

## Current stage

**M3 - Test Generation & Improvement: implemented and validated. M4 is active.**

M0 trust contracts and M1 ingestion boundaries remain binding. M2 adds deterministic audit,
traceability, atomic coverage, risk/scenario analysis and proposal-only local reports. See
`M2_EVIDENCE.md` for implemented semantics and validation evidence. M3 now provides complete
proposal-only manual authoring, non-destructive improvement, candidate derivation, renderers and
local CLI behavior. Linux and Windows CI passed for the M3 completion candidate; see
`M3_EVIDENCE.md`. No tag/release exists.

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
- Explicit greenfield, brownfield and clone/reuse M2 analysis dispatch.
- Requirement atomicity review without natural-language decomposition.
- Provenance-bearing criterion/test/state/actor/channel/risk/oracle traceability.
- Separate nominal-linkage and atomic-behavioral coverage with denominator reliability.
- Non-destructive existing-test, oracle, duplicate, stale, executability and history audit.
- Clone destination-evidence revalidation and separate reuse classifications.
- Evidence-activated risks and typed scenario universe with partition, boundary, decision,
  state-transition and bounded pairwise techniques.
- Deterministic scenario dispositions and proposal-only JSON/Markdown audit outputs.
- M3 draft/READY contracts, trust-safe oracle materialization, full evidence-supported procedures,
  greenfield/brownfield/clone proposals, revision diffs, Shared Step/Parameter candidates,
  risk-proportional evidence, canonical artifacts, static renderers and local `generate`/`render`
  CLI commands.
- M4.H1 typed provider-neutral reasoning requests/results with deterministic-only operation,
  explicit provider failure states, bounded fake-provider tests and no live-provider dependency.
- M4.H2 non-normative Candidate Semantic Records with exact request/result/source/provider/prompt/
  configuration/extractor cache binding, source mutation invalidation, provenance/authority tamper
  detection and cross-project isolation. This checkpoint is locally validated; branch CI and main
  integration remain pending.

## Current limitations

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
- Existing-test audit consumes explicit structured audit facts; it does not infer semantics from
  arbitrary historical prose.
- Conflict preservation is implemented; M1 does not choose authority or synthesize resolutions.
- H2 candidates are review artifacts only and are not yet normalized into the Project Model or
  connected to the ingestion CLI. Natural-language normalization begins in M4.H3.

## Deferred by milestone

- **M4 - Integrations & Production Agent Skill:** Azure/MCP/TMS adapters, preview/sync,
  target-drift/read-back/idempotency execution, production Agent Skill packaging, and the optional
  Semantic Reasoning Provider cataloged in `SEMANTIC_REASONING_ROADMAP.md`.
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
