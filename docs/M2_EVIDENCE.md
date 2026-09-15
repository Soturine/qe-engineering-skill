# M2 implementation evidence

Status: **implemented and validated for M2**. No release/tag created. Quality run
[`34970224467`](https://github.com/Soturine/qe-engineering-skill/actions/runs/34970224467)
passed on Linux and Windows for implementation commit `9403b81`. M0 trust contracts and M1
ingestion boundaries remain binding.

## Implemented pipeline

```text
validated M1 Project Model
  -> explicit greenfield/brownfield/clone dispatch
  -> explicit criterion atomicity review
  -> provenance-bearing traceability graph
  -> nominal and atomic behavioral coverage
  -> non-destructive existing-test/oracle/history audit
  -> evidence-activated risk records
  -> bounded scenario universe and dispositions
  -> proposal-only JSON and Markdown reports
```

`qe_skill.m2` is deterministic and local. It does not execute analyzed content, use a model,
access a network/TMS, generate final Test Cases, or mutate historical assets.

## Contracts and semantics

Versioned schemas cover the complete M2 report and standalone traceability, coverage, audit,
risk, scenario-universe and proposal artifacts. Every artifact carries project/snapshot identity;
the report binds to the canonical SHA-256 of the input Project Model. Cross-artifact references
and stale input bindings are mechanically validated.

Requirement atomicity reuses explicit `AtomicCriterion` nodes. Requirements without explicit
criteria receive `NO_EXPLICIT_ATOMS` and review findings; prose is never silently split.

Coverage states are `UNCOVERED`, `NOMINALLY_LINKED`, `PARTIALLY_COVERED`,
`BEHAVIORALLY_COVERED`, `BLOCKED_UNKNOWN`, and `CONFLICTING`. Reports expose separate counts
for requirement linkage and atom-level behavioral coverage. A denominator is marked reliable only
when required evidence is complete and every requirement has explicit atoms; otherwise no
percentage is fabricated.

Existing-test classifications implemented are `VALID_AS_IS`, `VALID_WITH_IMPROVEMENT`,
`PARTIAL_COVERAGE`, `AMBIGUOUS`, `BLOCKED_BY_SOURCE`, `DUPLICATE_INTENTIONAL`,
`DUPLICATE_REDUNDANT`, `CONFLICTING`, `STALE`, `OBSOLETE_CANDIDATE`, `UNTRACEABLE`, and
`NON_EXECUTABLE`. Clone output separately uses `REUSABLE`, `REQUIRES_UPDATE`,
`OBSOLETE_CANDIDATE`, `DUPLICATE`, `CONFLICTING`, and `UNKNOWN`.

Duplicate classification uses an exact structured signature across objective, criterion, layer,
actor, state, channel, data partition, risks, and oracle. Similar text alone is ignored. Explicit
intentional-regression metadata preserves intentional duplicates. Heuristic semantic similarity is
not implemented.

Oracle audit outcomes are `SUPPORTED`, `SUPPORTED_BUT_GROUPED`,
`IMPLEMENTATION_DERIVED_ONLY`, `CONFLICTING`, `STALE`, `AMBIGUOUS`, `UNSUPPORTED`, and
`BLOCKED_BY_SOURCE`. Historical Pass/Fail/Blocked counts remain operational evidence only and
never create an oracle or requirement.

## Scenario and risk support

The scenario universe supports explicit criterion dimensions, equivalence partitions, numeric/
length/cardinality boundary candidates, explicit decision rules, modeled state transitions,
deterministic bounded pairwise selection, and explicitly modeled risk records. Invalid transition
outcomes are not invented. Date arithmetic and inferred natural-language constraints are not
implemented.

Risk packs activate only from explicit `Risk` nodes. Risk scenarios have `RISK` origin and remain
exploratory without a defensible oracle. Configurable severity ordering supports deterministic
ranking without presenting unknown likelihood/detectability as precise scores. The optional human/
physical pack is available through explicit `human_physical` risks; no industrial assumptions are
hard-coded.

Dispositions preserve the full universe while marking scenarios selected, deferred, exploratory,
or blocked within configurable bounds. M2 produces improvement proposals for coverage,
preconditions, cleanup, traceability, grouped oracles, parameters, Shared Step candidates, stale
review, and risk scenarios. Proposals contain no external operations.

## Local automated evidence

The current local Windows run passes lint, format, strict mypy, **146 unit/component/integration
tests** and **32 evals**, including six M2 adversarial evals. One filesystem-symlink test skipped
because this Windows account lacks symlink privileges and remains enabled for capable CI runners.
The published PyPI advisory audit checked 22 locked packages with zero active findings at this
checkpoint; it is point-in-time evidence, not a guarantee of vulnerability absence. Dependency
pins did not change. The same checks passed on Linux and Windows CI, including installed-wheel
verification.

## Known limitations and M3+ boundary

- Audit facts beyond typed explicit fields are not inferred from arbitrary historical prose.
- Duplicate/conflict analysis is exact and conservative; heuristic similarity is deferred.
- Risk packs do not manufacture detailed outcomes; explicit model risks yield exploratory scenarios.
- Pairwise generation incrementally enumerates explicit value pairs and stops at the configured
  bound; when the bound is lower than the pair universe, deferred combinations remain implicit.
- M2 does not generate final manual Test Cases, full procedures, or replacement cases.
- No Azure DevOps, MCP, TMS publication, external CRUD, automation/execution, RAG/GraphRAG, or
  PR/change-impact analysis exists.

M2 does not modify existing historical assets. Risk-derived scenarios do not become requirements.
