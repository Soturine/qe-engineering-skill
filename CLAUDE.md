# CLAUDE.md — Claude Implementation and Audit Instructions

This repository is designed to be consumable by Claude and other Agent Skills-compatible runtimes. This file serves two purposes: implementation guidance and an explicit self-audit protocol.

## When implementing

Read `AGENTS.md` and all required documents listed there. Do not start from `SKILL.md` alone. The skill is the interface; the trust model, schemas, validators and evals are the safety boundary.

Before proposing or writing code:

- identify the current roadmap milestone;
- inventory affected contracts and schemas;
- inspect existing tests/evals;
- identify security, provenance and compatibility impacts;
- state assumptions explicitly.

If any required source/document cannot be read, report it. Do not silently continue as though it was studied.

## When auditing this repository

Treat the repository itself as the system under test. Do not simply summarize documentation. Attempt to disprove its safety claims.

Audit at least these dimensions:

1. **Source completeness:** Can the implementation claim completeness with missing/blocked sources?
2. **Provenance:** Can a generated oracle exist without a primary source pointer?
3. **Authority:** Can implementation silently override contract?
4. **Inference leakage:** Can `inferred=true` become a normative Expected Result?
5. **Prompt injection:** Can instructions inside analyzed project artifacts influence the agent's operating policy?
6. **Determinism:** Are deterministic checks delegated unnecessarily to model reasoning?
7. **Domain leakage:** Are example-project rules hard-coded into generic behavior?
8. **Provider lock-in:** Does core logic depend directly on one model/provider?
9. **Manual executability:** Can a READY test contain an unverified UI path, user role or impossible test data?
10. **Test quality:** Are duplicate scenarios rewarded as coverage?
11. **Mutation resistance:** Do changed source requirements change generated cases appropriately?
12. **Deletion resistance:** Does removal of evidence remove/reclassify dependent oracles?
13. **Contradiction handling:** Are conflicting authoritative sources surfaced rather than arbitrarily resolved?
14. **Security/privacy:** Can secrets or proprietary evidence leak into logs, fixtures or reports?
15. **Supply chain:** Are dependencies pinned/controlled and scripts safe by default?
16. **Reproducibility:** Is each run bound to source versions/hashes/commit identifiers?
17. **Observability:** Can a reviewer explain why a TC was generated, rejected or blocked?

## Required audit output

Use severity `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO` and provide for each finding:

- finding ID;
- evidence (file/symbol/line or reproducible command);
- violated invariant/policy;
- impact;
- reproduction;
- recommended fix;
- confidence.

End with one recommendation: `SHIP`, `FIX BEFORE MERGE`, or `BLOCK`.

Do not praise the repository without attempting adversarial cases. Do not manufacture findings merely to appear thorough.

## Skill audit

When `skill/qe-engineering/SKILL.md` becomes functional, audit it separately from the Python/core implementation:

- trigger quality and scope;
- progressive disclosure;
- instructions versus enforceable validators;
- context-window pressure;
- tool permissions;
- source discovery completeness;
- failure behavior;
- portability between Claude/Codex/Copilot-style runtimes;
- whether the skill can run on itself without recursive/indirection failure.

The goal is not to make the skill look good. The goal is to know when it is unsafe to trust.
