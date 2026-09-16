# M4 Evidence

Status: **H1-H3 validated; H4 implementation under validation; D1/H5-H11 not implemented**

This record is cumulative and reports only executable repository behavior.

## H1-H2 foundation

- typed bounded provider-neutral reasoning, including deterministic-only operation;
- explicit failure/timeout/rejection and a static offline provider;
- non-normative candidates bound to source/request/result/provider/prompt/config/extractor;
- exact cache identity, mutation invalidation and provenance/authority/scope validation.

## H3 - grounded multilingual semantic normalization

- typed meaning, concept, domain-term, alias, constraint, original-statement, normalized-record and
  normalization-set contracts;
- literal source text/language/span/hash/authority plus provider/run provenance preservation;
- explicit `FACT`, `OBSERVATION`, `CLAIM`, `HYPOTHESIS`, `DECISION` and `ORACLE` record kinds,
  all still non-normative review material;
- canonical labels require literal grounding and differing labels require alias relations;
- modality, polarity, constraints, grounded terms and quantitative guards affect comparison;
- typed failures for modal mismatch, lost negation, missing grounding and invalid structure;
- bounded `pt-BR`, `en`, `mixed` and `und` handling with no pre-translation;
- Portuguese/English Gherkin marker preservation and configurable project/output language;
- deterministic-only operation remains valid and requires no provider.

Unit/adversarial/eval coverage includes English and PT-BR paraphrases, obligation/permission,
prohibition/negation, required/optional, recommendation/requirement, actor, state and quantitative
mutations, Brazilian number punctuation, mixed Gherkin and technical identifiers. Retroactive
M0-M3 regressions cover PT-BR trust round-trip, mixed UTF-8 ingestion/spans and Portuguese
oracle/Expected Result rendering.

## Honest limitations after H3

- A matching key does not prove two requirements identical or authorize merging.
- Grounding proves cited words exist, not that an interpretation is correct.
- Language/modal detection is bounded; unknown forms stay unspecified rather than guessed.
- H3 accepts typed candidates but does not yet orchestrate arbitrary PRD/ADR/manual/backlog files;
  H5 owns that path.
- H6 questions, H7 wording gates, H8 local outputs, H9 production UX and
  H10-H11 end-to-end hardening remain unimplemented.

## H4 - semantic relations and adjudication

- bounded typed pairwise graph; no GraphRAG, vector database or hidden merge;
- consistent, conflicting, refinement, ambiguous and human-decision-required classifications;
- superseded/deployment-instance vocabulary reserved: lifecycle or matching implementation alone
  cannot prove a replacement/deployment link;
- exact normalized-record/set hash bindings and deterministic reconstruction validation;
- source authority/lifecycle context remains visible and cannot be downgraded without detection;
- provider disagreement and ambiguity require human review; confidence never selects a winner;
- conflicts are preserved, no facts are promoted and providers cannot self-authorize;
- PT-BR conflict/state evals verify that higher authority does not erase implementation divergence.

H4 reconstructs H3 inputs against their request, result, candidate set and current ledger.
Tampered authority, historical lifecycle edits, stale sources and cross-scope inputs are rejected.
Conflicts require human review. It does not yet promote accepted candidates into the
Project Model, ingest real documents or propagate downstream staleness; those are H5 boundaries.

H4 local validation (2026-09-16): 319 tests/evals passed, one Windows symlink-permission skip;
the same suite passed against the installed wheel. Ruff, formatting, mypy, pip check and dependency
audit passed. Wheel SHA-256: `e7231e872e6868aaeff8d462822bbcc822f4e6ad99361d1265dac9bbe54a0c8a`.
Remote Linux/Windows validation is pending at this checkpoint. No tag or release created.
