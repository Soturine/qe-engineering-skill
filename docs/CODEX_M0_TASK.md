# Codex Task — Implement M0 Foundations & Trust Model

Use this document as the first implementation handoff. It is intentionally generic and does not depend on any real project dataset.

## Objective

Implement **M0 — Foundations & Trust Model** from `ROADMAP.md` so the repository can mechanically reject unsupported normative test oracles and false completeness claims before any production test-case generator is built.

## Required reading

Follow `AGENTS.md`, then read:

- `ENGINEERING_CONSTITUTION.md`
- `IMPLEMENTATION_SPEC.md`
- `PROJECT_INPUT_CONTRACT.md`
- `SOURCE_AUTHORITY.md`
- `TRUST_MODEL.md`
- `ORACLE_POLICY.md`
- `PROJECT_MODEL.md`
- `QUALITY_GATES.md`
- `EVAL_STRATEGY.md`
- `SECURITY_THREAT_MODEL.md`

## Deliverables

Implement a Python package and CI-ready test suite containing:

1. versioned JSON Schemas for Run Manifest, Source Ledger, Claim/Provenance, Oracle, Approval, Risk, Project Model skeleton and Test Case;
2. typed domain objects or equivalent strongly validated structures;
3. deterministic cross-artifact validators for:
   - normative oracle provenance;
   - inference/approval rules;
   - completeness versus source study/read states;
   - project/snapshot isolation;
   - valid readiness transitions;
4. structured validation errors with stable codes and artifact references;
5. a minimal CLI that exercises real validators;
6. synthetic generic fixtures and tests for hard trust invariants;
7. basic CI configuration that runs formatting/lint/type checks as chosen plus unit/eval tests;
8. docs/status update reflecting what is actually implemented.

## Required negative tests

At minimum prove that the implementation rejects:

- a normative Expected Result with no source chain;
- an inferred normative oracle with no allowed approval/policy path;
- `COMPLETE` when a required source is `BLOCKED`, `NOT_STUDIED`, `PARTIALLY_STUDIED`, `TRUNCATED`, `FAILED` or `UNVERIFIED` as applicable;
- a source/claim/test artifact referencing another project/snapshot namespace;
- an approval record missing required attribution/scope.

Also prove that valid minimal fixtures pass.

## Constraints

- No real project/customer artifacts in fixtures.
- No production test generator yet.
- No RAG/GraphRAG/vector database.
- No bulk TMS writes.
- No live LLM required by deterministic-core tests.
- No provider-specific logic in domain code.
- Avoid overengineering; modular monolith/package first.

## Completion report

When finished, report:

- files added/changed;
- commands/tests executed;
- exact M0 exit criteria satisfied;
- remaining gaps/deferred work;
- security/provenance tradeoffs;
- current HEAD and CI status.

Do not mark M0 complete if any hard invariant is untested or failing.
