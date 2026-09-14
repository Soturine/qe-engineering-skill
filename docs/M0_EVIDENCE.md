# M0 implementation evidence

Status: partial. Package/tooling and version 1.0 typed/schema contracts implemented;
cross-artifact trust gates are pending.

The contracts cover run, ledger, claims, oracles, approvals/proposals, risk,
typed Project Model nodes and TMS-neutral manual Test Cases/Test Models.
Schema reproducibility, strict identity shapes and destructive-operation exclusion
have automated tests. This is not yet evidence that normative oracles are safe.

Python 3.12, setuptools packaging, Ruff, strict mypy and pytest form the initial
deterministic validation environment. CI runs the same checks without a model or TMS.
Direct tool dependencies and CI actions are pinned; a full transitive lock follows
when the trust-contract dependencies are established.

No generator, provider, source ingestion or external write adapter is present.
