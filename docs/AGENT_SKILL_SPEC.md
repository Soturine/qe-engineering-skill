# Agent Skill Specification

Status: **Target interface contract**

## Goal

Expose the stable quality-engineering engine through the open Agent Skills pattern without turning `SKILL.md` into a giant prompt or moving trust enforcement out of code.

The skill is a general quality-engineering interface. It must not assume a specific project, customer, domain, TMS, repository layout, process template or prior test-plan maturity.

## Target package

```text
skill/qe-engineering/
├── SKILL.md
├── references/
├── scripts/
└── assets/
```

`SKILL.md` is the orchestration interface. Schemas, validators and deterministic policy enforcement remain in the engine.

## Progressive disclosure

The skill should use concise activation metadata, load the minimum procedure needed, load reference material only for the active task, call deterministic scripts/validators when available, avoid copying the entire project corpus into model context, and produce structured artifacts plus a human-readable summary.

## Supported task families

Eventually:

- project evidence inventory;
- source-completeness report;
- Project Model extraction;
- requirements/test-plan audit;
- traceability/gap analysis;
- risk/scenario analysis;
- greenfield manual test-case generation;
- brownfield Test Case improvement with proposed step-by-step rewrites;
- clone/migration/reuse audit;
- TMS-neutral preview/export;
- optional TMS preview/sync;
- change-impact/regression selection;
- skill/repository self-audit.

## Connector independence

The core skill must work without Azure DevOps MCP, Azure DevOps REST, Jira, TestRail or any other TMS connection.

Without a live TMS connector, the skill can still:

- analyze local/exported PRDs, requirements, rules, use cases, ADRs and documentation;
- analyze repositories, code, migrations, API/event contracts, tests and configuration;
- analyze exported/manual test plans and historical artifacts supplied as files;
- build the Project Model;
- audit requirements and existing tests;
- identify coverage gaps, ambiguities, duplicates, conflicts and stale assumptions;
- generate new manual Test Cases;
- generate proposed detailed step-by-step rewrites for existing/cloned cases;
- generate Shared Step/parameter candidates;
- validate outputs through quality gates;
- render local Markdown/JSON/YAML/HTML-like previews/diffs.

A live TMS connector adds live discovery, live execution-history ingestion, external-ID reconciliation and optional publication/synchronization. It is not a prerequisite for the reasoning/audit/generation capabilities.

## Human-approval boundary

The skill is **proposal-first**.

Analysis, generation, auditing and preview are allowed without external write authority. External CRUD is never implied by model output.

Default lifecycle:

```text
Analyze
→ Generate / Audit
→ Validate
→ Preview / Diff
→ Human Review
→ Explicit Approval
→ Optional Adapter Write
→ Read-back Verification
```

No Test Case, requirement, Shared Step, comment, link, status, attachment or execution artifact may be created, edited, deleted, linked/unlinked or published merely because the model proposed it.

Approval must be:

- explicit;
- scoped to an exact operation set;
- bound to source/target snapshot identity;
- invalidated by relevant target drift before application.

Destructive operations are disabled by default and outside normal generation/audit flow.

## Required behavior

The skill must establish scope before completeness claims, surface inaccessible/truncated sources, separate contract/implementation/policy/risk/exploratory claims, stop normative generation when an oracle is unsupported, preserve conflicts, keep manual cases executable/source-backed, validate outputs before publication, preserve existing historical evidence, and require explicit approval for external modifications.

## Bias control / generality

The generic engine and committed fixtures must not encode project-specific rules, names, workflows, statuses, identifiers or expected outcomes.

Domain-specific behavior must be discovered from the active project's evidence or supplied through explicit optional domain packs/policies. Prior projects may inform reusable testing heuristics but never silently define truth for the current project.

## Portability

Provider/runtime-specific tool syntax belongs in adapters or thin wrapper instructions. The domain model must not depend on one model vendor or coding agent.

## Tool permissions

Start read-only where possible. Writes to repositories/TMS/external systems require explicit task intent, dry-run/preview for changes, scope validation, idempotency strategy, human approval and audit record.

## Failure modes

If the engine/validator required by the procedure is unavailable, the skill must not pretend its guarantees were enforced. It reports `NOT_VALIDATED` or an equivalent blocked capability and limits its claims.

If an optional connector is unavailable, connector-independent audit/generation capabilities remain available; only connector-specific features are blocked.

## Packaging discipline

Normative repository docs are the source of truth during development. A build/packaging step should select/version the necessary references into the skill package to avoid hand-maintained duplicated policy text.
