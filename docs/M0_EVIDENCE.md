# M0 implementation evidence

Status: **implemented and validated for M0**. No release/tag created.

## Deliverables and exit criteria

| Criterion | Implementation / automated evidence |
|---|---|
| Versioned schemas and domain contracts | `domain.py`, `schemas/v1/`; ten Draft 2020-12 schemas with reproduction tests |
| Unsupported normative oracle rejected | `validation.py`; missing/deleted/mutated/superseded/non-primary evidence tests |
| Required incomplete sources prevent COMPLETE | Study/read-state parameterizations, scope-reduction and false-completeness fixtures |
| Inference never silently becomes contract | Origin/inference tests, risk-invariant evals and explicit governed-promotion test |
| Project/snapshot isolation | Every artifact family tested in both dimensions; foreign cloned-oracle fixture |
| Explicit exact approval | Attribution/schema checks, trusted-context admission, altered actor/operations/preview/target/snapshot rejection |
| Evidence mutation invalidates approval | Same-snapshot ledger/claim-content digest mutation test |
| Explainable failures | Seven stable error-code families; structured CLI JSON and process-exit integration tests |
| Sufficient Project/Manual Model skeleton | Two entities/relationship, actor/role/group/permission, three states, normal/exception transitions, two channels, interface, atom, risk/ambiguity and manual fixture |
| Verified paths and readiness | Missing/inferred/invented paths, wrong types, order, unsupported actions/results, mappings and conflicts |
| Generic synthetic evals | Eleven reproducible fixtures; immutable history and inert prompt-injection tests |
| No live model/TMS required | Entire core suite runs offline; only dependency-advisory tooling accesses PyPI |
| Packaging and CI | Linux/Windows install, lint, strict typing, unit tests, evals and installed-wheel checks |

Current suite: **107 passing tests, including 22 evals**. The same suite runs against
editable source and installed wheels in CI. Published PyPI advisory audit: **20 pinned
packages, zero active findings** at the implementation checkpoint. This is a point-in-time
registry check, not a guarantee of vulnerability absence. Unavailable advisory metadata
or active findings fail CI.

## Reproduction

```text
python -m pip install -r requirements-dev.lock
python -m pip install --no-deps --no-build-isolation -e .
python -m pip check
python -m ruff check .
python -m ruff format --check .
python -m mypy
python -m pytest tests
python -m pytest evals
python -m tools.audit_dependencies
python -m pip wheel --no-deps --no-build-isolation --wheel-dir dist .
```

CI installs the wheel and repeats tests. Local Windows sandbox runs required execution
outside the sandbox for temporary-directory permissions and used `-p no:cacheprovider`
to avoid stale cache ACLs. No tests were skipped or weakened. Initial pytest/setuptools
pins had published advisories; pytest 9.0.3/setuptools 83.0.0 resolved them.

Regenerate with `python -m qe_skill.schemas` and `python -m evals.build_fixtures`.
Tests reject drift. Build archives are not committed or released.

## Architecture and limits

Strict Pydantic contracts and checked-in JSON Schemas share one versioned source.
Cross-artifact policy is separate from schema shape. Typed references include project
and snapshot; historical origin is opaque and cannot resolve as live evidence.
See `adr/0001-versioned-trust-contracts.md` and `CLI.md`.

Manual steps use exact oracle statements and verified-path claims. READY operational
text conservatively requires exact supporting text. Semantic paraphrase adjudication,
original-source authentication and full manual usability review remain future/human work.

Approval digests bind full approval/proposal content, operations, target versions and
ledger/claim bytes. Trusted context comes separately from the operator; M0 does not
authenticate humans or execute publication. Older pre-release proposals without the
new optional evidence digest still parse, but cannot authorize oracle promotion; rebuild
preview and obtain fresh approval as documented in `CLI.md`.

M0 does not inventory original files, detect every semantic contradiction, prove arbitrary
extracted statements true or guarantee undiscoverable-source completeness. These limits
are visible in CLI output and `STATUS.md`. Review-dependent cases remain non-READY.
Historical data and conflicts remain preserved, not silently rewritten.

No M1/M2 extraction, production generator, external CRUD, TMS/MCP, automation or retrieval
system was added. Only M0-required semantic/history/approval hooks anticipate later work.

## Commits

1. `8dfa41b` — package and quality baseline
2. `f7f4d69` — versioned schemas and domain models
3. `4ea59fb` — provenance, completeness and approval validators
4. `e767dcb` — Project Model integrity and manual readiness
5. `8053c05` — synthetic adversarial fixtures and evals
6. `1bdf73c` — bounded validation CLI
7. `08f10b5` — audited dependency pins and Linux/Windows wheel CI
8. `b7e6cf3` — evidence-content approval invalidation and conflict-resolution hardening

Each checkpoint was tested before commit, pushed to `main`, and checked with
`git rev-parse HEAD origin/main`. A subsequent documentation checkpoint records final
scope. Per-commit CI evidence is in the repository Actions history.
