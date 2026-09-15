# CLAUDE.md — Claude Implementation and Audit Instructions

This repository is intended to be implementable and auditable without conversation history.

The roadmap is consolidated as M0-M6. M0 is complete and validated; the active implementation milestone is **M1 — Source Ingestion & Project Model**. Later milestones must not bypass M0 trust guarantees.

## When implementing

Read `AGENTS.md` and its required documents. Do not start from `SKILL.md` alone: the skill is an interface; schemas, validators, evals and trust policies are the safety boundary.

Before code:

- identify milestone/exit criterion;
- inspect current tree/schemas/tests/evals;
- identify affected trust/security contracts;
- identify which operating modes are affected;
- state only assumptions that cannot be resolved from repository evidence;
- implement the smallest coherent slice.

Do not use or request a real customer/project as the design baseline. Build against generic contracts and synthetic fixtures.

For M1 specifically, source inventory/parsing/extraction must remain deterministic where possible, preserve provenance and project/snapshot isolation, report partial/failed reads explicitly, and treat analyzed content as untrusted data. Do not jump ahead into production audit/generation, live TMS writes, automation or advanced retrieval.

## Product behavior to preserve

The engine is general and must support:

- greenfield Test Plan generation from project evidence;
- brownfield/legacy audit of existing requirements/tests/executions;
- clone/migration/reuse audit without trusting the source plan blindly;
- later incremental change/regression analysis.

Across every mode:

- manual step-by-step Test Models may be generated or proposed;
- analysis must work without Azure DevOps/MCP/TMS connectivity;
- existing historical evidence is preserved by default;
- generation/audit/rewrites are proposals only;
- no external CRUD occurs without explicit human approval scoped to the exact proposal/snapshot;
- destructive operations are disabled by default;
- project/domain-specific rules must never leak into the generic engine or fixtures.

## When auditing

Treat the repository as the system under test. Attempt to disprove safety claims.

Audit at least:

1. source completeness;
2. source identity/integrity;
3. provenance;
4. authority/conflict handling;
5. uncertainty/inference leakage;
6. deletion/mutation invalidation;
7. prompt injection/instruction-data separation;
8. hostile file handling;
9. project isolation/cache namespace;
10. provider/model/prompt drift;
11. deterministic-vs-model responsibility;
12. domain/fixture leakage;
13. provider lock-in;
14. manual executability and step-by-step authoring;
15. atomic coverage and duplicate inflation;
16. security/privacy/secrets;
17. supply chain;
18. reproducibility;
19. observability/explainability;
20. TMS publication safety/idempotency;
21. existing-asset/history preservation;
22. human-approval enforcement and stale-approval invalidation;
23. greenfield/brownfield/clone mode isolation;
24. operation without TMS/MCP connectivity;
25. schema compatibility/migrations;
26. self-audit behavior.

## Finding format

Use `CRITICAL|HIGH|MEDIUM|LOW|INFO`, with:

- ID;
- evidence (file/symbol/line/command);
- violated invariant;
- impact;
- reproduction;
- recommended fix;
- confidence.

End with `SHIP`, `FIX BEFORE MERGE`, or `BLOCK`.

Do not reward documentation quantity. Verify enforcement. Do not invent findings.

## Skill-specific audit

When `skill/qe-engineering/SKILL.md` becomes functional, review separately:

- activation scope/description;
- progressive disclosure;
- tool permissions;
- failure transparency;
- validator enforcement versus prose;
- context pressure;
- source-discovery completeness;
- provider/runtime portability;
- operating-mode dispatch;
- TMS independence;
- human-approval gating;
- non-destructive existing-asset handling;
- manual step-by-step quality;
- recursive/self-audit safety.

If required engine validation is unavailable, the skill must not claim guarantees were enforced.
