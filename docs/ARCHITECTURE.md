# Architecture

## Architectural goals

The system must transform heterogeneous project evidence into a structured, auditable project model and then into high-confidence manual test cases. It must remain useful across web, API, mobile, data, embedded/IoT and industrial projects without hard-coded domain rules.

## Boundary rule

**Evidence discovery is not truth. Retrieval is not verification. Generation is not acceptance.**

The architecture separates these concerns deliberately.

## Modules

### 1. Source Inventory

Discovers configured repositories, documents, TMS items, tickets, API specifications, migrations, UI/design assets, configuration and integration artifacts. Produces immutable source identities, versions/hashes and expected-source status.

### 2. Parsers

Deterministic parsers for structured formats should be preferred. Code uses language-aware AST/symbol/dependency analysis where practical. Unstructured document extraction may use model assistance but must retain source location/provenance.

### 3. Authority & Provenance

Classifies source authority and tracks every derived claim back to primary evidence. Detects stale, contradictory and duplicate sources.

### 4. Project Model

Normalized graph/model of requirements, entities, fields, actors, roles, permissions, states, transitions, channels, APIs, integrations, constraints, timings, events, risks, ambiguities and existing tests.

### 5. Existing-Test Auditor

Analyzes test cases at atomic-criterion level rather than merely requirement-ID linkage. Detects ambiguous steps, grouped independent oracles, obsolete paths, duplicates, missing setup, inconsistent expected results and unexecutable scenarios.

### 6. Risk & Scenario Engine

Expands behavior into positive, alternate, negative, boundary, state-machine, authorization, security, concurrency, resilience, performance, accessibility and operational scenarios. Optional domain packs add physical/human factors without polluting the generic engine.

### 7. Scenario Optimizer

Maintains a comprehensive scenario map but avoids combinatorial explosion through equivalence classes, boundary analysis, state-transition coverage, decision tables, pairwise/combinatorial methods and risk ranking.

### 8. Test Case Generator

Generates structured **manual** cases from approved scenarios. The generator does not invent a missing oracle. Unsupported scenarios become ambiguity records or exploratory charters.

### 9. Quality Gate Validator

Machine-checks schema validity, provenance, source completeness, executability metadata, duplicate status and inference leakage. Human review handles semantic/authority decisions that cannot be safely automated.

### 10. Adapters

TMS adapters, starting with Azure DevOps Test Plans, convert the neutral model to native representations (steps, Expected Results, Shared Steps, parameters, tags, links). Provider/model adapters isolate external AI runtimes.

### 11. Evals & Observability

Golden fixtures, mutation suites, missing-source scenarios, contradictions, prompt injection, provider parity and self-audit runs. Structured run metadata enables comparison over time.

## RAG and GraphRAG

RAG is optional retrieval infrastructure, not a trust primitive. A vector index may miss a low-similarity exception. GraphRAG may help connect entities/claims across large document sets, but those claims are derived artifacts and must resolve back to primary sources.

Recommended order:

```text
inventory → deterministic parse → source graph → optional semantic retrieval/GraphRAG → primary-source verification → oracle/test model
```

For code, prefer AST/symbol/dependency graphs over generic document embeddings for structural facts.

## Data isolation

Indexes, caches, embeddings, run metadata and generated artifacts are scoped by project/snapshot. Cross-project retrieval is disabled by default.

## Future neutral intermediate representation

The long-term `TestModel` should support multiple renderers:

```text
TestModel
  ├─ Azure DevOps manual test
  ├─ Markdown/CSV report
  ├─ Gherkin
  ├─ Playwright/Appium
  ├─ API/integration tests
  ├─ pytest/JUnit
  └─ hardware/integration harness
```

Automation renderers must not redefine the oracle.
