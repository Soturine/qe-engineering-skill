# M3 Evidence — Partial Implementation

Status: **M3 PARTIAL**

Validated locally on Windows with Python 3.12.10. This document records implemented behavior and does not advance governance to M4.

GitHub Actions workflow `34979543111` passed on Linux and Windows for SHA
`0bc3e3cbb02200392bcb12177a753e0e8ad5f80e`.

## Implemented

- Versioned contracts separate unresolved authoring proposals from strict `TestCase` artifacts.
- Exact current CONTRACT/POLICY claims may become normative oracles; IMPLEMENTATION remains characterization and RISK/EXPLORATORY remains non-normative.
- Selected M2 scenarios produce deterministic, traceable, proposal-only drafts with explicit blockers.
- Fully supplied supported context passes the existing READY validator before materialization.
- Brownfield and clone proposals preserve historical assets; clone assumptions are checked against destination evidence.
- Typed Shared Step/Parameter candidates and deterministic JSON/YAML/Markdown/escaped-HTML renderers exist.
- `qe generate` binds Project Model, M2 report and configuration hashes, rejects stale/cross-scope input and performs local writes only.
- Fifteen M3 adversarial evals cover the required trust boundaries.

Historical assets are never modified. Risk-derived scenarios do not become requirements or normative Expected Results.

## Validation

- pip check, Ruff, format and strict mypy: passed
- tests: `180 passed, 1 skipped`
- evals: `47 passed`
- dependency audit: `22` packages, no findings
- installed wheel `qe_engineering_skill-0.3.0-py3-none-any.whl`: `227 passed, 1 skipped`

The Windows skip is the existing symlink-privilege test and remains enabled in CI.

## Missing exit criteria

1. Multi-step procedures are not yet synthesized from every supported verified path; the current authoring slice uses one validated operational step.
2. Brownfield records field/step diffs and rationale but does not yet build a complete replacement procedure for every M2 defect class.
3. Candidate discovery does not yet consume every M2 partition/repeated-setup source.
4. Evidence expectations are represented but not fully varied by risk severity.
M3 therefore remains active. Package version remains `0.3.0`; M4 is not activated and no tag/release is authorized.

## Preserved limitations

Arbitrary prose is not semantically normalized; PDF/DOCX parsing and full OpenAPI reference resolution remain absent; source authorship is not authenticated; M3 neither publishes nor executes tests; full downstream invalidation/change impact remains M6; risk-only scenarios stay exploratory.
