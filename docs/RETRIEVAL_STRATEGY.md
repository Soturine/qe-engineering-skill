# Retrieval and Knowledge Strategy

Status: **Architecture policy**

## Principle

Retrieval improves discovery. It does not establish completeness or truth.

## Required order

```text
scope declaration
    ↓
deterministic source inventory
    ↓
snapshot / hashes / identities
    ↓
structured parsers + AST/symbol analysis
    ↓
source/claim graph
    ↓
lexical + semantic retrieval as needed
    ↓
optional GraphRAG/graph retrieval
    ↓
primary-source verification
    ↓
Project Model / oracle / Test Model
```

## Deterministic baseline first

Before adding vector search or GraphRAG, the engine must be able to enumerate every in-scope source, report read/integrity failures, hash/version sources, extract structured formats deterministically, build basic code symbol/import/dependency facts for supported languages, and prove which sources were and were not analyzed.

A semantic index cannot replace this.

## RAG

Use RAG for finding likely supporting spans across large corpora, surfacing aliases/similar concepts, narrowing model context and discovering related requirements/tests.

Do not use top-K retrieval as proof that all relevant evidence was considered.

## GraphRAG / knowledge graphs

Use only when evals demonstrate benefit for cross-document relationships, global questions, entity/claim linkage or impact analysis. Graph/LLM-generated entities and claims remain derived artifacts. Any normative oracle must resolve back to primary evidence.

## Code understanding

Prefer language-aware AST/symbol/import/dependency graphs for structural code facts. Embeddings may complement them for semantic search but must not replace deterministic symbol identity.

## Cache/index correctness

Every index/cache/embedding namespace is bound to project ID, snapshot/run identity, source hash/version, parser/index version and embedding/model version when relevant. Changed or deleted evidence invalidates dependent derived artifacts. Stale cache reuse must be detectable.

## Retrieval fallback

If a connector, index or model is unavailable, report the degradation. Do not silently substitute an older cache, another provider or a broader source scope unless the run records the change and re-evaluates completeness.
