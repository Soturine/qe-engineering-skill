# M0 implementation evidence

Status: partial. Package/tooling and version 1.0 typed/schema contracts implemented;
provenance, completeness and exact-scope approval checks implemented.
Project Model integrity and manual readiness checks are implemented.
Synthetic adversarial evals and the four-command CLI are implemented.

CLI checkpoint: 103 tests pass. Inputs are bounded UTF-8 JSON; malformed inputs,
duplicate keys, oversized/deep inputs and unsupported remote schema references fail
with structured errors. Integration tests verify process exit codes and omission
of raw sensitive statements. See `CLI.md` for invocation and trust boundaries.

At this checkpoint 88 tests pass, including 22 evals. Prompt-injection content is
inert data; validation preserves input/history. Risk promotion needs an exact
authoritative invariant or separately attested human approval. Role mappings must
be confirmed before use in READY execution. Unresolved conflicts block even a
standalone normative oracle. Remote CI is green through the integrity checkpoint.

Integrity checks cover typed references, duplicate IDs, entity/state ownership,
unresolved affected conflicts, verified paths and executable READY prerequisites.
The representative synthetic model contains two entities, actor/role/group mapping,
three states, normal/exception transitions, two channels, an interface, atomic
criterion, risk-only scenario, ambiguity and an evidence-backed manual case.

Trust checks reject missing/mutated/superseded/non-primary evidence, source authority
leakage, unsupported inference, scope reductions, false completeness and stale or
self-declared approvals. Tests include valid minimal chains and governed promotion.

The contracts cover run, ledger, claims, oracles, approvals/proposals, risk,
typed Project Model nodes and TMS-neutral manual Test Cases/Test Models.
Schema reproducibility, strict identity shapes and destructive-operation exclusion
have automated tests. This is not yet evidence that normative oracles are safe.

Python 3.12, setuptools packaging, Ruff, strict mypy and pytest form the initial
deterministic validation environment. CI runs the same checks without a model or TMS.
Direct tool dependencies and CI actions are pinned; a full transitive lock follows
when the trust-contract dependencies are established.

No generator, provider, source ingestion or external write adapter is present.
