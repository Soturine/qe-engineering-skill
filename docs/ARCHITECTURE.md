# Architecture

## Goal

Transform heterogeneous project evidence into a structured, auditable Project Model and then into high-confidence manual test cases. Remain useful across web, API, mobile, data, embedded/IoT and industrial projects without hard-coded real-project rules.

## Boundary rule

**Discovery is not truth. Retrieval is not verification. Generation is not acceptance.**

## Modules

### 1. Scope & Source Inventory
Discovers configured repositories/documents/TMS/work items/contracts/configuration/integration artifacts and produces stable identities, snapshot metadata and study/read status.

### 2. Safe Ingestion & Parsers
Deterministic parsers for structured formats; bounded/sandboxed handling for hostile content; language-aware AST/symbol/dependency analysis for supported code.

### 3. Authority, Provenance & Lifecycle
Tracks every claim to primary evidence, source authority/freshness/supersession, uncertainty and conflicts.

### 4. Project Model
Normalized model of requirements, entities, actors/permissions, states/transitions/channels, interfaces, integrations, constraints, timings, configuration, risks, ambiguities, conflicts and existing tests.

### 5. Existing-Test Auditor
Analyzes atomic behavior rather than requirement-ID linkage only. Detects grouped independent oracles, ambiguous/non-executable steps, duplicates, stale paths, missing setup and unsupported Expected Results.

### 6. Risk & Scenario Engine
Expands positive/alternate/negative/boundary/state/permission/security/concurrency/resilience/performance/accessibility/operational scenarios. Domain packs are opt-in.

### 7. Scenario Optimizer
Preserves the scenario universe while selecting a defensible executable set using equivalence, boundaries, decision tables, state coverage, pairwise/combinatorial methods and risk ranking.

### 8. Manual Test Generator
Builds structured manual Test Models only from approved/supported scenarios. Missing oracle becomes ambiguity/exploration, not invented Pass/Fail.

### 9. Quality Gate Validator
Machine-checks schema, source completeness, provenance, inference leakage, model integrity, manual executability, isolation and publication safety. Human review handles semantic authority decisions where needed.

### 10. Provider Boundary
Typed model-provider adapters support bounded extract, relate, synthesize and scenario-probe work
without embedding one vendor into the core. Requests bind exact project/snapshot evidence excerpts,
hashes, limits and prompt/config versions. Results bind provider/model/adapter identity and expose
failure/timeout states. Outputs remain untrusted proposals until candidate and trust gates validate
them. Deterministic-only operation requires no provider.

### 11. TMS / Output Adapters
Azure DevOps first, later other TMS/report/automation renderers. Adapters cannot redefine Test Model semantics.

### 12. Evals & Observability
Synthetic golden/mutation/deletion/conflict/prompt-injection/isolation/provider-parity/self-audit suites and structured run metadata.

## Retrieval

See `RETRIEVAL_STRATEGY.md`.

```text
scope → inventory → snapshot → deterministic parse/AST
      → source/claim graph → optional semantic/GraphRAG discovery
      → primary-source verification → Project Model/Test Model
```

## Data isolation

Every cache/index/embedding/run/output is scoped by project + snapshot + relevant parser/model versions. Cross-project retrieval is off by default.

## Neutral Test Model

```text
TestModel
  ├─ Azure DevOps manual
  ├─ Markdown/CSV/report
  ├─ Gherkin
  ├─ browser/mobile automation
  ├─ API/integration tests
  ├─ unit/test-framework renderers
  └─ hardware/integration harness
```

Automation renderers must not redefine the oracle.

## Deployment posture

Start as a modular monolith and CLI/library. Distributed services, graph databases or always-on infrastructure require measured justification.
