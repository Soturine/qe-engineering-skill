# M3 Evidence — Test Generation & Improvement

Status: **M3 IMPLEMENTED AND VALIDATED**

The validated completion candidate is `a887d755a5c2be4d62d1305b69679d42b705e853`.
GitHub Actions workflow `35004416200` passed on Linux and Windows. Package version is `0.4.0`.
No tag or release was created.

## Implemented authoring behavior

- `GREENFIELD`, `BROWNFIELD`, and `CLONE_REUSE` consume an exact validated M1 Project Model and
  M2 report. Input project/snapshot identities and canonical hashes are bound into every report.
- Typed drafts retain unresolved path, actor, data, environment, build, cleanup, isolation, or
  oracle evidence. A strict `TestCase` is materialized only after existing READY validation passes.
- Complete verified paths become deterministic ordered preparation/navigation/action/validation
  procedures. Partial paths retain only supported steps and block instead of inventing navigation.
- Normative Expected Results exactly preserve current validated CONTRACT or
  ORGANIZATIONAL_POLICY oracles. IMPLEMENTATION remains characterization; RISK and EXPLORATORY
  cases have no normative Pass/Fail unless independently supported.
- Pass, Fail, and Blocked rules are explicit. Evidence expectations keep normal Pass lightweight,
  add diagnostic context for Fail/Blocked, and strengthen review/evidence for explicitly modeled
  high/critical risks without requiring screenshots by default or creating a new oracle.
- Brownfield output preserves original identity, text, hash, and history while emitting KEEP,
  IMPROVE, REVISE, or REPLACE proposals with field/step diffs and evidence-backed rationale.
  Unsupported repair remains blocked; missing coverage remains a separate proposed case.
- Clone/reuse proposals revalidate destination requirement, criterion, actor, state, channel,
  path, data/assumption, and oracle references. Source-project behavior is never destination truth.
- Shared Step candidates require repeated, stable, evidence-backed setup; core validation and
  execution results are not shared. Parameter candidates retain explicit constraints, partitions,
  values, provenance, and used-by links without fabricating identifiers or credentials.

Historical assets are never modified. Risk-derived scenarios do not become requirements or
normative Expected Results. All M3 artifacts remain proposal-only and perform no external write.

## Canonical artifacts and renderer

`qe generate` writes canonical `m3-generation-report.json`, Test Model JSON/YAML, traceability,
manifest, improvement, Shared Step, and Parameter artifacts plus requested Markdown/static HTML
review views. JSON is the source of truth. `qe render` deterministically re-renders an existing
canonical report without rerunning authoring or reasoning.

The component-oriented static HTML view conditionally displays cases, steps, Expected Results,
readiness/blockers, Shared Steps, Parameters, brownfield original/proposed diffs, traceability,
risks/gaps, and generation metadata. Cross-links connect candidates with using cases. It escapes
untrusted content, has no remote assets or JavaScript dependency, tolerates additive version-1
fields, and rejects incompatible schema majors. `ReportTheme` can explicitly change project name,
accent, and density as presentation metadata only; no theme is inferred from project content.

Validation rejects stale or foreign upstream input, dangling generated references,
non-consecutive steps, Expected Result/oracle mismatch, invalid READY cases, risk-to-normative
leakage, and a Test Model that differs from materialized proposals.

## Validation evidence

Validated locally on Windows with Python 3.12.10 and in workflow `35004416200`:

- pip check: passed
- Ruff lint and format check: passed
- strict mypy: passed
- unit/component/integration/schema/CLI tests: `197 passed, 1 skipped`
- adversarial evals: `52 passed`
- dependency audit: `22` packages, no findings
- installed wheel `qe_engineering_skill-0.4.0-py3-none-any.whl`: `249 passed, 1 skipped`
- Linux CI: passed
- Windows CI: passed

The local Windows skip is the existing symlink-privilege test. It remains enabled and passed on a
capable CI runner. Synthetic fixtures are generic and reproducible.

## Preserved limitations and milestone boundary

Arbitrary prose remains structural rather than automatically normalized into requirements;
PDF/DOCX semantic parsing and full OpenAPI reference resolution are absent; source authorship is
not authenticated; duplicate semantics remain conservative. M3 neither publishes nor executes
tests and implements only direct upstream-hash stale detection, not full change impact.

The optional Semantic Reasoning Provider remains M4 work. The revised roadmap places whole-system
audit, advanced retrieval and change impact in M6 immediately after M4, followed by Azure/MCP/TMS
adapters and automation/execution in M5. See `ROADMAP.md` for current allocation.
