# M0 implementation evidence

Status: partial. Package/tooling baseline only; trust contracts and gates are not yet implemented.

Python 3.12, setuptools packaging, Ruff, strict mypy and pytest form the initial
deterministic validation environment. CI runs the same checks without a model or TMS.
Direct tool dependencies and CI actions are pinned; a full transitive lock follows
when the trust-contract dependencies are established.

No generator, provider, source ingestion or external write adapter is present.
