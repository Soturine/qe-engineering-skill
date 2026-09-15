# Implementation Status

## Current stage

**M0 — Foundations & Trust Model: implemented and validated.**

M0 completion covers deterministic contracts and gates, not production generation or
project understanding. See `M0_EVIDENCE.md` for tests, boundaries and exit criteria.
The current commit must remain green in CI.

The implementation roadmap is now consolidated as M0-M6. The earlier finer-grained
M0-M10 plan was regrouped without removing planned capabilities.

## Implemented

- Python 3.12+ typed modular-monolith package; no model/TMS runtime dependency.
- Ten reproducible version 1.0 JSON Schemas and equivalent strict domain contracts.
- Ledger/manifest completeness, authority, provenance and namespace validation.
- Source mutation/deletion, inferred-oracle and exact-content approval checks.
- Typed Project Model skeleton, reference integrity and duplicate detection.
- TMS-neutral Manual Test Model and deterministic readiness gates.
- Four bounded, read-only JSON validation CLI commands with structured errors.
- Eleven synthetic fixtures, unit/integration tests and adversarial evals.
- Linux/Windows CI, transitive pins, published-advisory audit and installed-wheel tests.

## Partial by design

- Source authenticity/semantics: M0 checks declared metadata, hashes and provenance
  chains. It does not inspect original evidence or independently discover scope.
- Approval: exact bindings and separate trusted-context admission are checked;
  human authentication, signing, durable storage and external enforcement are deferred.
- Manual executability: structural prerequisites and source-backed instructions are
  checked; humans still evaluate feasibility, usability and meaning.
- Operating modes: metadata/history/model shapes exist; workflow dispatch is deferred.
- Conflicts: unresolved conflicts block affected normative output; M0 does not choose
  precedence or synthesize resolutions. Supplied resolutions need authority.

## Deferred by consolidated milestone

- **M1 — Source Ingestion & Project Model:** inventory/parsers, document extraction,
  AST/symbol inventory, semantic extraction/normalization, Project Model population and
  source conflict/alias/staleness handling.
- **M2 — Audit, Traceability & Risk Analysis:** existing-test audit, atomic coverage,
  duplicate/conflict/stale classification, risk/scenario generation and coverage optimization.
- **M3 — Test Generation & Improvement:** production manual generator/rewriter,
  greenfield plans, missing-case generation and step-by-step rewrite proposals.
- **M4 — Integrations & Production Agent Skill:** Azure/MCP/TMS adapters, preview/sync,
  target-drift/read-back/idempotency execution and production Agent Skill packaging.
- **M5 — Automation & Execution Assistance:** automation renderers and optional bounded
  execution/evidence-capture assistance.
- **M6 — Advanced Retrieval & Change Impact:** RAG/GraphRAG evaluation, richer code
  dependency graphs, PR/diff impact analysis and regression selection.

M0-M3 are intended to form a useful standalone product that works from local/exported
evidence without requiring Azure DevOps, MCP or another TMS.

The only adjacent foundations already present are M0-required semantic nodes, historical
identity and approval/proposal hooks. No later-milestone execution capability is currently implemented.

## Safety interpretation

Validation executes no analyzed content and preserves its inputs. Destructive operations
are absent from the normal proposal contract. Historical identity cannot resolve as
destination evidence. Passing validation or READY never grants publication authority.
Actual TMS history preservation must be tested when a writer exists; M0 claims no live
integration guarantee. Cases needing review remain non-READY pending human workflow.
