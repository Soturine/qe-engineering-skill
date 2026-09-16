# M4 Evidence

Status: **H1-H3 implemented and validated; H4-H11 not implemented**

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
- H4 relation/adjudication, H6 questions, H7 wording gates, H8 adapters, H9 production UX and
  H10-H11 end-to-end hardening remain unimplemented.
