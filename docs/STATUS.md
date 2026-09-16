# Implementation Status

## Current stage

**M0-M3 and M4.H0-H4 are validated. M4.D1 is validated and frozen for presentation.**

M0 trust contracts and M1 ingestion boundaries remain binding. M2 adds deterministic audit,
traceability, atomic coverage, risk/scenario analysis and proposal-only local reports. See
`M2_EVIDENCE.md` for implemented semantics and validation evidence. M3 now provides complete
proposal-only manual authoring, non-destructive improvement, candidate derivation, renderers and
local CLI behavior. Linux and Windows CI passed for the M3 completion candidate; see
`M3_EVIDENCE.md`. No tag/release exists.

The accepted `M4_PRODUCT_KISS_ADDENDUM.md` governs the H3-H11 product shape and KISS
sequencing. It is a target contract; only capabilities listed below as implemented are current.

The product contract is agent-first: Agent Skill + AI agent is the primary experience,
`qe run`/`qe doctor` is secondary, and the deterministic trust engine is the foundation.
Production Agent Skill orchestration remains M4.H5-H11 work; this hierarchy does not imply those
checkpoints are already implemented.

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
  detection and cross-project isolation. This checkpoint is implemented and validated on Linux
  and Windows.
- M4.H3 grounded multilingual normalization preserves literal source language/text/span/hash/
  authority and provider/run provenance; requires grounded canonical labels plus explicit aliases;
  and distinguishes record kind, modality, polarity, constraints and domain terms. PT-BR, English,
  mixed text and bilingual Gherkin have synthetic regression/eval coverage.
- PT-BR surface guards additionally preserve temporal-order, quantitative-direction,
  exclusivity/exception and measured-quantity signals; explicit maximum/minimum reversal is
  rejected. Normalization failures can produce unanswered, provenance-bound clarification
  artifacts in the configured output language.
- M3 generation localizes engine-owned Test Case titles, rules, rationales, readiness notes and
  evidence instructions when `output_language=pt-BR`, while source-backed actions, Expected
  Results and technical identifiers remain literal.
- M4.H4 bounded semantic relation/adjudication graphs preserve conflicts and authority context,
  require human review for conflicts/ambiguity/provider disagreement, reject stale or tampered H3
  envelopes, ignore confidence as a winner selector,
  and never promote facts or self-authorize providers.
  Optional provider `RELATE` candidates are provenance-bound, visible and review-only; deterministic
  relations remain authoritative for mechanically verifiable comparisons.
- M4.D1 Technical Preview implementation provides an offline self-contained HTML review, PT-BR
  presentation, complete available Test Case fields, searchable/filterable cases, navigable
  evidence/traceability, visible gaps/reviews/H4 conflicts and a reproducible synthetic demo.
  Linux and Windows CI passed; H5 remains the next checkpoint after presentation.

## Current limitations

- Arbitrary natural-language documents are structurally parsed but not yet orchestrated into H3
  typed candidates. Real-document semantic orchestration is H5 work.
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
- H3/H4 records remain review artifacts and are not promoted into the Project Model or connected
  to the ingestion CLI. Real-world orchestration and downstream stale propagation begin in M4.H5.
- Clarification generation currently covers semantic-normalization issues only; answer binding,
  interactive resume and broader H6 question categories remain deferred.
- D1 can render H4 conflicts supplied in a validated review context, but the current `generate`
  command does not yet orchestrate H3/H4 from arbitrary natural-language documents (H5).

## Deferred by milestone

- **M4 - Semantic QE & Production Agent Skill:** D1 local Technical Preview before presentation;
  H5-H11 real-document orchestration, questions/oracle quality, local outputs and production skill.
- **M5 - Automation & External Integrations (after M6):** TMS/Azure adapters, preview/sync,
  explicit approval, drift/read-back/idempotency and bounded execution/evidence-capture assistance.
- **M6 - Advanced Retrieval & Change Impact:** RAG/GraphRAG evaluation, richer code dependency
  graphs, PR/diff impact analysis and regression selection.

## Safety interpretation

Inventory/parsing executes no analyzed content and preserves its inputs. Destructive operations
are absent. Historical identity cannot resolve as destination evidence. Passing M1 validation
does not prove source authenticity, arbitrary semantics, undiscoverable-source completeness,
human executability or publication authority. Unknown, partial and conflicting evidence remains
visible rather than being replaced with an inferred fact.
