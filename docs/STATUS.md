# Implementation Status

This file prevents architecture documentation from being mistaken for implemented capability.

## Current stage

**Foundation/specification — M0 not yet implemented in code.**

## Documented

- product/trust architecture;
- Engineering Constitution;
- Project Input Contract;
- source authority and provenance model;
- oracle policy;
- Project Model target;
- quality gates;
- operating modes: greenfield, brownfield/legacy audit, clone/migration/reuse, incremental regression;
- manual Test Case authoring contract, including detailed human step-by-step proposals;
- existing-asset/history-preservation policy;
- human-approval boundary for all external writes;
- TMS independence of the core engine;
- test-design/risk/human-physical policies;
- security threat model;
- eval strategy and quality metrics;
- retrieval/RAG/GraphRAG position;
- Azure DevOps adapter contract;
- Agent Skill target interface;
- public benchmark/market research;
- implementation/audit instructions.

## Not yet implemented

- Python package/domain engine;
- JSON Schemas;
- Source Ledger/Run Manifest validators;
- Project Model builder;
- parsers/AST inventory;
- model-provider adapters;
- operating-mode runtime dispatch;
- existing Test Plan importer/auditor;
- scenario/risk engine;
- manual test-case generator/rewriter;
- local JSON/YAML/Markdown Test Model renderers;
- Azure DevOps read/write adapter;
- human-approval persistence/enforcement in executable code;
- production Agent Skill runtime;
- automation renderers;
- RAG/GraphRAG;
- CI/eval execution.

## Important safety status

The repository currently **documents** that generation/audit/rewrite are proposal-producing operations and that no external CRUD occurs without explicit human approval. This policy is not yet mechanically enforced because the runtime/adapter does not exist.

Likewise, non-destructive treatment of existing Test Cases, requirements, runs, comments, screenshots/attachments and history is a target contract, not yet executable behavior.

## Rule

Until code/tests/evals exist, documentation may describe **target behavior** only. Auditors and coding agents must not infer implementation from the existence of a policy document.

The next actionable documents are `AGENTS.md`, `docs/IMPLEMENTATION_SPEC.md` and `docs/CODEX_M0_TASK.md`.
