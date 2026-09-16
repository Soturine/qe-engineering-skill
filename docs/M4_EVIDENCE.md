# M4 Evidence

Status: **H1-H4 and D1 validated; Technical Preview frozen; H5-H11 not implemented**

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
- optional `RELATE` provider candidates retain their exact H2 envelope/hash, must cite both record
  sources, remain separate from deterministic classification and cannot override it;
- conflicts are preserved, no facts are promoted and providers cannot self-authorize;
- PT-BR conflict/state evals verify that higher authority does not erase implementation divergence.

H4 reconstructs H3 inputs against their request, result, candidate set and current ledger.
Tampered authority, historical lifecycle edits, stale sources and cross-scope inputs are rejected.
Conflicts require human review. It does not yet promote accepted candidates into the
Project Model, ingest real documents or propagate downstream staleness; those are H5 boundaries.

H4 local validation (2026-09-16): 319 tests/evals passed, one Windows symlink-permission skip;
the same suite passed against the installed wheel. Ruff, formatting, mypy, pip check and dependency
audit passed. Wheel SHA-256: `e7231e872e6868aaeff8d462822bbcc822f4e6ad99361d1265dac9bbe54a0c8a`.
Remote Linux/Windows validation passed at `8ed0bdb7c6233e6db6c5e0e0d2695f06932f6ef3`, workflow
`35058770837`. No tag or release created.

## D1 - Technical Preview UX

- static single-file HTML with embedded CSS/JavaScript, no server/CDN/framework/network;
- project/output language resolution with PT-BR default for PT-BR projects;
- presentation labels and engine-owned messages localized without translating evidence, oracle
  wording or technical identifiers;
- overview counts without invented percentages; complete available Test Case proposal fields;
- case search, readiness/review filters, responsive layout, visible focus and non-color labels;
- internal requirement/criterion/risk/scenario/evidence/case links where exact references exist;
- validated review context rejects stale/tampered/cross-scope Project Model, M2 or H4 inputs;
- conflicts show both candidate statements, authority context, adjudication, human-review state and
  the honest limitation that affected tests are not linked by H4 yet;
- synthetic PT-BR demo builder and concise reproduction instructions under
  `examples/technical-preview/`.

D1 local validation (2026-09-16), including the final H4 provider-relation addendum: 327 tests/evals passed against source and the installed wheel,
with one Windows symlink-permission skip. Ruff, formatting, mypy, schema reproduction, pip check,
dependency audit and the reproducible demo smoke passed. Wheel SHA-256:
`38b5c73081f7616d293db1a50072c998dc59abf9e6c89f1e5baff116fbad3c45`.
Final Linux/Windows validation passed at `65528974a72a4994be3490424b303d70ea5de388`, workflow
`35060484764`. D1 does not implement H5 real-document semantic
orchestration, `qe run`, `qe doctor`, a live provider or any external write.

## Post-D1 PT-BR cross-cutting increment

- bounded surface signals now retain PT-BR modality, negation, temporal order, maximum/minimum,
  exclusivity/exception, measured quantities and Gherkin without pre-translation;
- a candidate cannot reverse an explicit `no máximo`/`no mínimo` direction;
- semantic-normalization failures can produce unanswered, provenance-bound PT-BR clarification
  artifacts without fabricating an answer or authority;
- generated M3 Test Models localize engine-owned titles, rules, rationales, blockers and evidence
  instructions for `output_language=pt-BR`, while evidence/oracles/paths/technical identifiers
  remain literal;
- the product contract now explicitly makes Agent Skill + AI agent the primary experience,
  CLI secondary and the deterministic trust engine the foundation. This does not claim H5-H11 or
  the production Agent Skill are complete.

Local validation (2026-09-16): 334 passed, one expected Windows symlink-permission skip; Ruff,
format check, strict mypy, schema reproduction, `pip check`, dependency audit and an isolated
installed-wheel PT-BR/CLI smoke passed. The wheel was built with the repository-supported
`pip wheel --no-build-isolation` path because the optional `build` frontend is not installed in
the development venv. Wheel SHA-256:
`749e3b091f7b98a42854823badd6ca9725004aa7bd211c1bc9123491a4434f98`. Remote Linux/Windows CI is
pending for this increment.
