# Multilingual and PT-BR Policy

Status: **cross-cutting product invariant**

The engine is multilingual. Brazilian Portuguese (`pt-BR`) is a first-class supported language,
English (`en`) is supported, and a source or excerpt may be `mixed` or `und` (undetermined).
Technical identifiers remain literal and are never translated.

## Language contract

- `source_language` belongs to each source or bounded excerpt and never changes authority.
- `project_locale` configures the project's normal human language.
- `output_language` is independently configurable as `source`, `pt-BR` or `en`.
- canonical identifiers may be stable and language-neutral/English-like.
- original evidence, Unicode, accents, source/span/hash and authority metadata are always preserved.
- translation, summaries and canonical labels never replace primary evidence.

A normal PT-BR project may set `project_locale = pt-BR` and `output_language = pt-BR` while code,
APIs, fields, enums, classes and other identifiers remain English or mixed.

## Milestone invariants

- **M0:** provenance/trust preserves literal multilingual evidence; language never grants authority.
- **M1:** structural parsing remains language-independent and UTF-8 text/spans remain literal.
- **M2:** semantic rules, conditions, permissions, prohibitions, states, time and boundaries must not
  assume English. Provider-assisted interpretation remains candidate-only.
- **M3:** human-authored Action/Expected Result/oracle text may remain PT-BR; renderers must not
  force translation or reinterpret an approved oracle.
- **M4:** normalization, adjudication, questions, wording, adapters and production skill UX support
  PT-BR/mixed inputs and independently configured output language.
- **M5:** automation consumes the approved Test Model without language-driven reinterpretation.
- **M6:** retrieval/change impact must evaluate cross-language meaning drift, including modality,
  negation, actors, temporal order, states and quantitative limits.

## KISS implementation rule

Deterministic formats, AST, schemas, routes, IDs and hashes stay language-independent. Small
locale-aware hints may protect explicit modality, negation and quantities, but they are never an
authority or a substitute for semantic interpretation. Ambiguous language goes to an optional
provider as original text and returns a non-normative candidate. Do not build a large regex
dictionary or require pre-translation.

## H3 baseline

H3 recognizes bounded `pt-BR`, `en` and `mixed` language signals; preserves literal source text;
distinguishes Portuguese obligation, prohibition, permission, optionality, condition and
recommendation markers; protects negation and locale-formatted quantities; and records Portuguese
and English Gherkin markers. Unknown language remains `und` and does not block structural parsing.

The bounded recognizer is intentionally incomplete. Grounding proves that cited wording exists,
not that a probabilistic interpretation is correct. Human review and all authority gates remain.
