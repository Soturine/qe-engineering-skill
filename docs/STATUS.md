# Implementation Status

## Current stage

**M0 — Foundations & Trust Model: implemented and validated.**

M0 completion covers deterministic contracts and gates, not production generation or
project understanding. See `M0_EVIDENCE.md` for tests, boundaries and exit criteria.
The current commit must remain green in CI.

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

## Deferred

M1 inventory/parsers; M2 extraction/normalization and graph/matrix construction;
M3 existing-test audit; risk/scenario generation and coverage optimization; production
manual generator/rewriter; providers; Azure/MCP/TMS; publication, target-drift checks,
read-back and idempotency execution; production Agent Skill; automation; RAG/GraphRAG.

The only adjacent foundations are M0-required semantic nodes, historical identity and
approval/proposal hooks. No later-milestone execution capability was introduced.

## Safety interpretation

Validation executes no analyzed content and preserves its inputs. Destructive operations
are absent from the normal proposal contract. Historical identity cannot resolve as
destination evidence. Passing validation or READY never grants publication authority.
Actual TMS history preservation must be tested when a writer exists; M0 claims no live
integration guarantee. Cases needing review remain non-READY pending human workflow.
