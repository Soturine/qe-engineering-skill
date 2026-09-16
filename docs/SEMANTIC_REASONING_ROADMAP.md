# Semantic Reasoning Roadmap

Status: **M4 implementation plan; H1-H3 provider, candidate/cache and grounded multilingual normalization implemented and validated**

The target architecture is hybrid: deterministic structure first, bounded heuristic discovery
second, and an optional semantic provider only where natural-language interpretation adds value.
Provider output is a candidate interpretation, never authority.

## FSR-01 — Hybrid ingestion

Status: **typed H3 normalization implemented; real-document orchestration remains H5**

Documents, Git, OpenAPI, tests and history flow through bounded deterministic extraction of text,
structure, hashes, spans and symbols. Cheap heuristics may propose obvious identifiers, Gherkin
shapes and route/method hints. An optional provider may then propose requirements, rules, actors,
states, constraints, relationships, conflicts and source-support locations. Schema validation and
M0 trust gates decide whether candidates enter the Project Model or require review.

Never implement `source → model assertion → normative truth`.

## FSR-02 — Candidate Semantic Records

Status: **implemented and validated in M4.H2**

Candidates retain type, statement/value, source reference/hash/span/symbol, interpretation class
(`explicit`, `structural`, `heuristic`, `inferred`, `unresolved`), confidence, inferred flag,
provider/model/version, operation type, material prompt/template/config version and reproducible
run identity. They are schema-validated and cannot raise certainty, change authority or discard
provenance.

## FSR-03 — Responsibility by reasoning cost

Status: **DEFERRED_TO_M4**

- Deterministic: JSON, YAML, OpenAPI, Python AST, explicit `qe_model`, schemas, IDs, hashes, spans,
  symbols and exact route/method declarations.
- Heuristic: low-risk discovery hints only; a match is never authority.
- Semantic provider: PRDs, manuals, ADRs, free-form requirements, ambiguity and cross-document
  semantic relationships.

Use the cheapest reliable layer and avoid model calls for already-structured facts.

H3 adds non-normative normalized records with explicit record kind, modality, polarity,
constraints, grounded domain terms and alias relations. PT-BR is first-class and mixed technical
identifiers remain literal. Comparable keys never imply identity, authority or approval. See
`MULTILINGUAL_POLICY.md`, `M4_EVIDENCE.md` and ADR 0003.

## FSR-04 — M4 Semantic Reasoning Provider

Status: **provider-neutral boundary implemented in M4.H1; live provider adapters not implemented**

M4 owns a typed, bounded `ReasoningProvider` boundary for extraction, relation and synthesis
requests/results. Deterministic-only operation remains available. Real project inputs may produce
candidate semantics, but only validated evidence-backed records feed the existing M2/M3 pipeline.

## FSR-05 — Optional procedure wording

Status: **DEFERRED_TO_M4**

After deterministic M3 has selected the scenario, actor, verified path and oracle, an optional
provider may improve human-readable wording. Validation must reject or downgrade wording that
introduces unsupported navigation, fields, roles, behavior or certainty.

## FSR-06 — Variant ownership

Status: **DEFERRED_TO_M4**

M2 discovers explicit scenario structure, partitions and boundary variants. M3 packages them into
separate or parameterized Test Cases using bounded diagnosability/coverage rules. A provider may
not create unbounded Cartesian suites.

## FSR-07 — Governed Shared Steps and Parameters

Status: **DEFERRED_TO_M4**

Semantic assistance may propose grouping or wording, while deterministic admissibility remains
authoritative. Shared Steps must be repeated, stable, path-compatible setup and never share
execution outcomes. Parameters must preserve explicit partitions/constraints and never fabricate
values.

## FSR-08 — No self-authorization

Status: **DEFERRED_TO_M4**

Runtime gates remain deterministic: oracle/path/source/snapshot/scope integrity, step order,
risk/implementation leakage, candidate provenance/confidence and history preservation. Human
review remains available for `READY_WITH_REVIEW`, `AMBIGUOUS` and `BLOCKED_SOURCE`. A provider is
never its own authority or approver.

## FSR-09 — Automation consumes the approved model

Status: **DEFERRED_TO_M5**

M5 automation candidates trace to the approved Test Model and its oracle. Automation must test
the same behavior and may not silently replace or reinterpret Expected Results.

## FSR-10 — Responsibility map

| Layer | Responsibility |
|---|---|
| Deterministic parser | Structure and explicit facts |
| Heuristic extractor | Cheap discovery hints, never authority |
| Semantic provider | Candidate natural-language interpretation |
| M0 | Trust, provenance, approval and isolation |
| M1 | Evidence-backed Project Model |
| M2 | Audit, coverage, risks, scenarios and variants |
| M3 | Executable manual Test Models |
| Optional wording provider | Improve only supported procedure wording |
| Validators | Reject invention, stale/cross-scope and bypass conditions |
| Renderer | Canonical JSON to review formats without reasoning |
| M4 | Local semantic QE, production skill and human outputs |
| M5 | Approved-model automation/execution and external TMS adapters, after M6 |
| M6 | Change impact, benchmarks, independent audit and hardening |

The LLM may interpret or synthesize, but authority remains evidence, provenance, source authority,
deterministic validators and explicit approval/review.

## FSR-11 — Semantic-mode benchmark

Status: **DEFERRED_TO_M6**

Benchmark deterministic-only, deterministic-plus-heuristics and provider-assisted modes on the
same fixtures and contracts. Measure recall and mapping quality together with false requirements,
provenance/span accuracy, unsupported-oracle/hallucinated-path rates and efficiency. See
`M6_CATALOG.md`.

## FSR-12 — Provider efficiency and cache binding

Status: **exact candidate cache identity implemented in M4.H2; provider-call orchestration remains incremental**

Use deterministic facts first, heuristics for cheap hints and the provider for genuine semantic
ambiguity. Cache only with exact source hash, provider/model/version, prompt/template/config and
project/snapshot binding. Mutation invalidates extraction. Progressive depth never weakens trust.

## FSR-13 — Real-project usability

Status: **DEFERRED_TO_M4**

The long-term flow accepts project documents, repositories, APIs, tests and history without
requiring users to hand-author every `qe_model` record. Candidate semantics remain provenance-bound
before M2 audit, M3 generation, M4 local output, M6 change impact and later M5 sync/automation.

## FSR-14 — Retrospective provider audit

Status: **DEFERRED_TO_M6**

Tier 1 M6 audit attempts false requirements, conflict merging, modal strengthening, invented
actors/paths, raised confidence, lost spans, implementation-to-contract leakage, stale cached
semantics and review bypass. Accepted findings follow reproduce → failing test/eval → fix → full
validation → benchmark regression.
