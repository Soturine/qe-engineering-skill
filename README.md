# QE Engineering Skill

Evidence-first, manual-first quality engineering for software, APIs, mobile, data, IoT and industrial systems.

This repository defines a vendor-neutral Agent Skill and supporting contracts for auditing a project from its actual evidence, mapping behavior and risk, and generating high-confidence manual test cases with explicit provenance. Automation is a future output of the same test model, not the starting point.

## Core principle

> **No normative Expected Result without a traceable oracle. No claim of completeness without a verifiable source inventory. No silent inference.**

The project is intentionally stricter than a prompt that says “read the requirements and generate test cases.” Its goal is to make the reasoning auditable and mechanically reject outputs that were built from incomplete, contradictory or unsupported evidence.

## What the system will do

1. Inventory every in-scope project source and freeze a reproducible snapshot.
2. Record what was studied, blocked, intentionally excluded or not yet studied.
3. Parse requirements, rules, use cases, ADRs, source code, database migrations, API contracts, UI assets, tests, configuration, integrations, tickets and operational documents.
4. Build a normalized project knowledge model before generating tests.
5. Separate contractual truth from observed implementation, organizational policy, risk-derived scenarios and exploratory hypotheses.
6. Audit the existing test plan for atomic coverage, contradictions, duplicates, obsolete assumptions, missing context and non-executable steps.
7. Expand coverage using state transitions, decision tables, boundaries, negative paths, permissions, security, concurrency, resilience, time, data integrity, accessibility and—when applicable—human/physical-process risks.
8. Optimize the scenario set for coverage and risk instead of maximizing test count.
9. Generate manual test cases with reproducible preconditions, test data, exact actions, objective expected results, Fail/Blocked semantics, cleanup and source traceability.
10. Pass every generated case through quality gates and human review before TMS publication.
11. Export to Azure DevOps Test Plans through an adapter without coupling the core model to Azure.
12. Reuse the same approved intermediate model for future automation adapters.

## Trust classes

| Origin | Meaning | Normative Pass/Fail? |
|---|---|---:|
| `CONTRACT` | Approved requirement, business rule, use case, acceptance criterion, protocol or equivalent authority | Yes |
| `IMPLEMENTATION` | Behavior confirmed in source, schema, migration, runtime, tests or current manual | Yes for characterization/regression; not automatically a business requirement |
| `ORGANIZATIONAL_POLICY` | Explicit engineering, security or quality policy | Yes within its declared scope |
| `RISK` | Scenario derived from a credible failure mode | Only when a defensible invariant/oracle exists; otherwise review is required |
| `EXPLORATORY` | Important hypothesis without a sufficient oracle | No; exploratory charter only |

## Source completeness

Every run maintains a `SOURCE_LEDGER`. Each expected source must be one of:

- `STUDIED`
- `NOT_STUDIED`
- `BLOCKED`
- `OUT_OF_SCOPE`

A run may continue with blocked sources, but it **must not call itself complete**. Missing access is surfaced explicitly.

## Manual-first execution model

The first production target is a human tester. A READY case must answer without guesswork:

- What must already exist?
- Which environment, user/profile and permissions are required?
- Where is the action performed?
- Which data must be prepared?
- What exactly is done?
- What objectively counts as correct?
- What is Fail versus Blocked?
- Which evidence is useful when a deviation occurs?
- What must be cleaned up?
- Which primary source supports every Expected Result?

A normal Pass should remain lightweight. Evidence collection should be proportional to risk and primarily required for deviations, blocked cases, critical controls or explicit audit obligations.

## High-level architecture

```text
Source inventory + immutable snapshot
              ↓
Deterministic parsing / code symbol analysis
              ↓
Authority + provenance + conflict detection
              ↓
Normalized project model
              ↓
Existing-test audit + traceability graph
              ↓
Risk/state/decision/boundary expansion
              ↓
Scenario optimization + deduplication
              ↓
Manual test-case generation
              ↓
Quality gates + human review
              ↓
TMS adapters (Azure DevOps first)
              ↓
Execution feedback / regression selection
              ↓
Future automation adapters
```

RAG or GraphRAG may assist discovery on large corpora, but neither is a source of truth. Any claim used as a test oracle must resolve back to primary evidence.

## Repository map

- `AGENTS.md` — implementation contract for coding agents such as Codex, Claude Code and Copilot.
- `CLAUDE.md` — Claude-specific operating and audit instructions.
- `docs/ARCHITECTURE.md` — target architecture and boundaries.
- `docs/ENGINEERING_CONSTITUTION.md` — engineering rules for this repository.
- `docs/TRUST_MODEL.md` — evidence, confidence, provenance and completeness model.
- `docs/ORACLE_POLICY.md` — rules for Expected Results and ambiguities.
- `docs/QUALITY_GATES.md` — mechanical and human release gates.
- `docs/TEST_DESIGN_POLICY.md` — scenario design and optimization rules.
- `docs/RISK_MODEL.md` — cross-project risk taxonomy.
- `docs/HUMAN_PHYSICAL_FACTORS.md` — optional industrial/physical-operation pack.
- `docs/BENCHMARKS.md` — public tools/skills studied and design lessons.
- `docs/ROADMAP.md` — incremental milestones.
- `docs/AUDIT_GUIDE.md` — how a reviewer or another agent audits this repository.
- `docs/AI_IMPLEMENTATION_GUIDE.md` — how an implementation agent must continue the project.
- `schemas/` — machine-verifiable contracts.
- `skill/qe-engineering/SKILL.md` — Agent Skills interface; intentionally thin until the foundations are implemented.
- `evals/` — golden, mutation, contradiction and anti-hallucination evaluation fixtures.

## Current milestone

**M0 — Foundations & Trust Model.**

No production test-case generator should be implemented until the source ledger, provenance model, oracle policy, schemas, validators and evaluation strategy are stable enough to reject unsupported output.

See [ROADMAP](docs/ROADMAP.md).
