# Documentation Index

Use this page as the canonical reading map.

## Start here

1. `../README.md` — product purpose and current status.
2. `../AGENTS.md` — implementation contract for coding agents.
3. `ENGINEERING_CONSTITUTION.md` — non-negotiable engineering principles.
4. `IMPLEMENTATION_SPEC.md` — implemented M0/M1 build boundaries.
5. `M0_EVIDENCE.md` and `M1_EVIDENCE.md` — executable milestone evidence.
6. `ROADMAP.md` — milestone sequence and exit criteria.
7. `STATUS.md` — what is documented versus actually implemented.

## Product operation modes

- `OPERATING_MODES.md` — greenfield generation, brownfield audit, clone/migration reuse and incremental regression modes, all with human approval before external writes.
- `EXISTING_ASSET_AUDIT_POLICY.md` — non-destructive audit and history-preservation rules for existing requirements/tests/runs/comments/screenshots/links.
- `MANUAL_TEST_AUTHORING.md` — canonical operational step-by-step structure for human-executable manual Test Cases.

## Evidence and trust

- `PROJECT_INPUT_CONTRACT.md` — scope, snapshots, study/read states and hostile-input boundary.
- `SOURCE_AUTHORITY.md` — precedence, lifecycle, conflicts and authority rules.
- `TRUST_MODEL.md` — Source Ledger, provenance, confidence, completeness and readiness.
- `ORACLE_POLICY.md` — what can become an Expected Result.
- `PROJECT_MODEL.md` — normalized intermediate representation.
- `QUALITY_GATES.md` — readiness/publication/release gates.

## Test design and risk

- `TEST_DESIGN_POLICY.md` — scenario design, atomicity, manual steps, Pass/Fail/Blocked.
- `RISK_MODEL.md` — cross-project risk taxonomy.
- `HUMAN_PHYSICAL_FACTORS.md` — optional physical/human-operation pack.
- `QUALITY_METRICS.md` — trust, coverage and test-quality metrics.
- `STANDARDS_BASELINE.md` — how external standards may and may not be used.

## Architecture, retrieval and security

- `ARCHITECTURE.md`
- `RETRIEVAL_STRATEGY.md`
- `SECURITY_THREAT_MODEL.md`
- `AGENT_SKILL_SPEC.md`
- `AZURE_DEVOPS_ADAPTER.md`

## Validation and independent review

- `EVAL_STRATEGY.md`
- `M0_EVIDENCE.md`
- `M1_EVIDENCE.md`
- `AUDIT_GUIDE.md`
- `AI_IMPLEMENTATION_GUIDE.md`
- `../CLAUDE.md`

## Public research

- `BENCHMARKS.md` — specific public skills/tools and adopted lessons.
- `MARKET_LANDSCAPE.md` — broader public quality-engineering direction.

## Machine-contract scaffolding

- `../schemas/README.md`
- `../evals/README.md`
- `../skill/qe-engineering/SKILL.md`

## Rule for coding agents

If a document describes a capability but `STATUS.md` says it is unimplemented, treat it as a target contract—not existing behavior. Implement milestone exit criteria in order rather than attempting the entire architecture in one change.
