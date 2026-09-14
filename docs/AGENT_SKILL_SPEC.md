# Agent Skill Specification

Status: **Target interface contract**

## Goal

Expose the stable quality-engineering engine through the open Agent Skills pattern without turning `SKILL.md` into a giant prompt or moving trust enforcement out of code.

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
- manual test-case generation;
- TMS preview/export;
- change-impact/regression selection;
- skill/repository self-audit.

## Required behavior

The skill must establish scope before completeness claims, surface inaccessible/truncated sources, separate contract/implementation/policy/risk/exploratory claims, stop normative generation when an oracle is unsupported, preserve conflicts, keep manual cases executable/source-backed, validate outputs before publication, and require explicit approval for configured high-consequence actions.

## Portability

Provider/runtime-specific tool syntax belongs in adapters or thin wrapper instructions. The domain model must not depend on one model vendor or coding agent.

## Tool permissions

Start read-only where possible. Writes to repositories/TMS/external systems require explicit task intent, dry-run/preview for bulk changes, scope validation, idempotency strategy and audit record.

## Failure modes

If the engine/validator required by the procedure is unavailable, the skill must not pretend its guarantees were enforced. It reports `NOT_VALIDATED` or an equivalent blocked capability and limits its claims.

## Packaging discipline

Normative repository docs are the source of truth during development. A build/packaging step should select/version the necessary references into the skill package to avoid hand-maintained duplicated policy text.
