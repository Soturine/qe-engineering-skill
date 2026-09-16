# ADR 0003: grounded multilingual semantic normalization

Status: accepted for M4.H3.

H3 normalizes validated Semantic Candidates into comparable, non-normative records. A normalized
record retains cited text, detected/declared source language, source/span/hash/authority identity,
the H2 candidate hash, interpretation class, provider/run metadata and review state. It cannot
become a Project Model fact or oracle.

Canonical actor, capability, intent and domain-term labels require literal source forms and exact
excerpt references. When a label differs from source wording, an explicit alias relation is
required; source wording is never replaced. Constraints likewise require literal grounding. This
proves support location, not semantic correctness, so provider interpretations remain candidates.

Record kind, modality, polarity, constraints and grounded domain terms participate in comparison
identity. Deterministically observed modal, negation and quantitative markers protect distinctions
that a provider must not erase. PT-BR is first-class, English and mixed text are supported, and
unknown language remains explicit. `pode` represents permission/capability (`MAY`), never a
universal synonym for optionality. Unsupported structure becomes a typed issue rather than a
guessed fallback.

Equivalent comparison keys express comparable candidate meaning, not requirement identity or
authority equivalence. The normalizer accepts the provider-neutral H2 contract and also operates
directly on typed deterministic/heuristic candidates. No live provider, translation, NLP stack,
TMS, network call or external write is required. Real-document orchestration remains H5 work.
