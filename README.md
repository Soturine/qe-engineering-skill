# QE Engineering Skill

Evidence-first, manual-first quality engineering for software, APIs, mobile, data, IoT and industrial systems.

This repository specifies a vendor-neutral Agent Skill and supporting engine contracts for auditing a project from its actual evidence, mapping behavior and risk, and generating high-confidence manual test cases with explicit provenance. Automation is a later output of the same approved Test Model, not the starting point.

## Core principle

> **No normative Expected Result without a traceable oracle. No claim of completeness without a verifiable source inventory. No silent inference.**

The goal is not to produce the largest test suite. The goal is to produce the smallest defensible, executable set that covers relevant behavior and risk—and to explain exactly why every normative expectation exists.

## Product contract

The system will eventually:

1. declare analysis scope and inventory every discoverable in-scope source;
2. freeze/version a reproducible snapshot where possible;
3. record studied, partial, blocked, superseded and out-of-scope evidence honestly;
4. parse requirements, rules, use cases, ADRs, code, migrations, API/event/data contracts, UI/design artifacts, tests, configuration, integrations, work items and operational docs;
5. build a normalized Project Model **before** test generation;
6. separate contractual truth, technical contracts, implementation observations, organizational policy, risk-derived scenarios and exploratory hypotheses;
7. audit existing tests at atomic-criterion level for gaps, contradictions, duplicates, stale assumptions and non-executable steps;
8. map the wider scenario/risk universe (state, decision, boundary, permissions, security, concurrency, resilience, time, data, accessibility and optional physical/human factors);
9. optimize coverage rather than maximize test count;
10. generate manual test cases with reproducible preconditions/data/actions, observable Expected Results, Fail/Blocked semantics, cleanup and provenance;
11. validate every case through deterministic quality gates and configured human review;
12. render approved cases to TMS adapters (Azure DevOps first) without coupling the core to one TMS;
13. ingest execution feedback as operational evidence;
14. later render the same approved Test Model to automation frameworks without changing oracle semantics.

## Trust/origin classes

| Origin | Meaning | Normative Pass/Fail? |
|---|---|---:|
| `CONTRACT` | approved product/business/regulatory/technical obligation | Yes |
| `IMPLEMENTATION` | behavior confirmed in code/schema/runtime/tests | Characterization/regression only unless separately approved |
| `ORGANIZATIONAL_POLICY` | explicit engineering/security/quality policy | Yes within declared scope |
| `RISK` | scenario derived from a credible failure mode | Only with a defensible invariant or explicit approval |
| `EXPLORATORY` | important hypothesis without sufficient oracle | No; charter/question only |

Authority, confidence and freshness are separate dimensions. See `docs/SOURCE_AUTHORITY.md`.

## Completeness

Every run maintains a `SOURCE_LEDGER`. A required source may be `STUDIED`, `PARTIALLY_STUDIED`, `NOT_STUDIED`, `BLOCKED`, `OUT_OF_SCOPE` or `SUPERSEDED`, with independent read-integrity metadata.

A run may continue when evidence is unavailable, but it must downgrade its completeness claim and surface the gap. “Complete” means all required sources in the explicit, discoverable/configured scope are accounted for—not omniscience about artifacts that were never discoverable.

## Manual-first execution model

A `READY` manual case must answer without guesswork:

- what must already exist;
- environment/build/snapshot;
- actor/profile/permissions;
- verified execution path;
- data properties to prepare;
- exact human action;
- observable correct result;
- what is Pass, Fail and Blocked;
- evidence expectations proportional to risk;
- cleanup/isolation;
- which primary evidence supports every normative Expected Result.

## High-level architecture

```text
scope + deterministic source inventory
              ↓
snapshot / identity / integrity
              ↓
parsers + AST/symbol analysis
              ↓
authority + provenance + conflict detection
              ↓
normalized Project Model
              ↓
existing-test audit + atomic traceability
              ↓
risk/scenario universe
              ↓
optimization + deduplication
              ↓
manual Test Model generation
              ↓
quality gates + human review
              ↓
TMS renderers (Azure first)
              ↓
execution feedback / change impact
              ↓
future automation renderers
```

RAG/GraphRAG may assist discovery later. They never replace source inventory or primary-source verification.

## Repository map

Core guidance:
- `AGENTS.md` — implementation contract for coding agents.
- `CLAUDE.md` — Claude-specific implementation/audit instructions.
- `docs/ENGINEERING_CONSTITUTION.md` — normative engineering rules.
- `docs/IMPLEMENTATION_SPEC.md` — concrete build order for M0+.
- `docs/ROADMAP.md` — milestones and exit criteria.

Trust/evidence:
- `docs/PROJECT_INPUT_CONTRACT.md`
- `docs/SOURCE_AUTHORITY.md`
- `docs/TRUST_MODEL.md`
- `docs/ORACLE_POLICY.md`
- `docs/PROJECT_MODEL.md`
- `docs/QUALITY_GATES.md`

Test/risk:
- `docs/TEST_DESIGN_POLICY.md`
- `docs/RISK_MODEL.md`
- `docs/HUMAN_PHYSICAL_FACTORS.md`
- `docs/QUALITY_METRICS.md`

Architecture/integration:
- `docs/ARCHITECTURE.md`
- `docs/RETRIEVAL_STRATEGY.md`
- `docs/AGENT_SKILL_SPEC.md`
- `docs/AZURE_DEVOPS_ADAPTER.md`
- `docs/SECURITY_THREAT_MODEL.md`

Validation/research:
- `docs/EVAL_STRATEGY.md`
- `docs/AUDIT_GUIDE.md`
- `docs/BENCHMARKS.md`
- `docs/MARKET_LANDSCAPE.md`
- `docs/AI_IMPLEMENTATION_GUIDE.md`

Machine contracts/scaffolding:
- `schemas/`
- `evals/`
- `skill/qe-engineering/SKILL.md`

## Current implementation status

**Foundation/specification stage.**

The repository currently defines the trust architecture, research baseline and M0 implementation plan. A production test-case generator is intentionally **not** considered implemented until the Source Ledger, schemas, validators and hard-invariant evals are executable.

Start with `AGENTS.md` and `docs/IMPLEMENTATION_SPEC.md`.
