# CLAUDE.md — Claude Implementation and Audit Instructions

This repository is intended to be implementable and auditable without conversation history.

## When implementing

Read `AGENTS.md` and its required documents. Do not start from `SKILL.md` alone: the skill is an interface; schemas, validators, evals and trust policies are the safety boundary.

Before code:

- identify milestone/exit criterion;
- inspect current tree/schemas/tests/evals;
- identify affected trust/security contracts;
- state only assumptions that cannot be resolved from repository evidence;
- implement the smallest coherent slice.

Do not use or request a real customer/project as the design baseline. Build against generic contracts and synthetic fixtures.

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
14. manual executability;
15. atomic coverage and duplicate inflation;
16. security/privacy/secrets;
17. supply chain;
18. reproducibility;
19. observability/explainability;
20. TMS publication safety/idempotency;
21. schema compatibility/migrations;
22. self-audit behavior.

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
- recursive/self-audit safety.

If required engine validation is unavailable, the skill must not claim guarantees were enforced.
