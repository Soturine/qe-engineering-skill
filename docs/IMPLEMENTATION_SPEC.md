# Implementation Specification for Coding Agents

Status: **Build plan**

This document exists so a coding agent can implement the repository without relying on conversation history or a specific example project.

The roadmap is consolidated as M0-M6. Earlier references to separate parsing, knowledge-model, audit, risk, integration, skill, automation and execution milestones are now grouped into larger product outcomes without removing planned capability.

## Target repository shape

```text
qe-engineering-skill/
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── docs/
├── schemas/
├── src/qe_skill/
│   ├── domain/
│   ├── inventory/
│   ├── parsers/
│   ├── provenance/
│   ├── project_model/
│   ├── traceability/
│   ├── risk/
│   ├── scenario/
│   ├── generation/
│   ├── validation/
│   ├── providers/
│   └── adapters/
├── skill/qe-engineering/
│   ├── SKILL.md
│   ├── references/
│   ├── scripts/
│   └── assets/
├── evals/
└── tests/
```

Do not create empty packages merely to look complete. Add modules when their milestone begins.

## Product-mode constraints

The architecture must support, without project-specific hard-coding:

- greenfield test design from project evidence;
- brownfield/legacy audit of existing requirements/tests/results;
- clone/migration/reuse audit;
- later incremental regression/change-impact analysis.

The core must work without Azure DevOps, MCP or any TMS connection. External systems are optional adapters.

Generation/audit/rewrite are proposal-producing operations. They do not imply CRUD authority. Any external write path must require an explicit, scoped human approval and must preserve historical evidence by default.

## Consolidated milestone map

- **M0 — Foundations & Trust Model:** deterministic contracts, validators, schemas, evals, CLI and CI.
- **M1 — Source Ingestion & Project Model:** inventory, parsing, extraction and normalized evidence-backed project understanding.
- **M2 — Audit, Traceability & Risk Analysis:** existing-test audit, atomic traceability, risk/scenario analysis and coverage optimization.
- **M3 — Test Generation & Improvement:** greenfield generation plus missing-case and step-by-step rewrite proposals.
- **M4 — Integrations & Production Agent Skill:** optional TMS/Azure adapters and portable Agent Skill packaging.
- **M5 — Automation & Execution Assistance:** approved-model renderers and optional bounded execution assistance.
- **M6 — Advanced Retrieval & Change Impact:** retrieval experiments, richer dependency analysis and regression/change-impact selection.

## M0 implementation order

1. Establish package/tooling and CI.
2. Implement typed domain objects or validated mappings for Run Manifest, Source Ledger, Claim/Provenance, Oracle, Approval, Risk, Test Case and a Project Model skeleton.
3. Add JSON Schema validation.
4. Add cross-field policy validators that schemas cannot express safely.
5. Implement hard gates:
   - reject normative oracle without provenance;
   - reject normative inferred oracle without allowed approval/policy path;
   - reject `COMPLETE` when a required source is incomplete;
   - reject invalid project/snapshot isolation;
   - reject invalid approval scope/attribution;
   - reject verified path claims without evidence where represented.
6. Create synthetic fixtures and adversarial tests.
7. Add structured error/result types; do not use exceptions as the only user-facing diagnosis.
8. Add CLI only when it exercises real validators, for example `qe validate-ledger`, `qe validate-oracle`, `qe validate-project-model`, `qe validate-test-case`.
9. Keep Agent Skill scaffold thin until M0 exit criteria are executable.
10. Update docs/status honestly.

## M0 exit criteria

M0 is complete only when automated tests prove:

- unsupported normative oracles are rejected;
- incomplete required sources prevent `COMPLETE`;
- inference cannot silently become contract;
- project/snapshot IDs are enforced;
- approval records are explicit and scoped rather than implicit generation side effects;
- validation errors identify the violated rule and artifact;
- schemas and validators are versioned;
- synthetic eval policy is followed;
- no live model is required to test deterministic core behavior;
- no TMS/MCP connection is required to exercise core trust contracts.

## M1 implemented boundary

M1 adds deterministic local inventory, M0 Source Ledger population, bounded parsers for
Markdown/text/JSON/YAML/OpenAPI/Python, typed extraction records, conservative Project Model
population and local CLI artifacts. Only explicit `qe_model` records and raw OpenAPI structural
declarations create semantic nodes. Natural-language structure and Python symbols remain evidence;
they are not guessed into requirements, routes, roles or business rules.

Unsupported, unreadable, partial, mutated and root-escaping evidence remains explicit and prevents
false completeness. The implementation has no live model, retrieval database, network reference
resolution, TMS dependency or publication capability. See `M1_EVIDENCE.md` for exact supported
types, automated evidence and limitations.

## Project Model design expectations

The M0 skeleton must leave room for structured, provenance-bearing nodes for:

- entities, fields, constraints, relationships;
- actors, roles, groups, permissions;
- states, transitions, channels, actions/events, guards/exceptions;
- interfaces/integrations;
- requirements and atomic criteria;
- invariants;
- ambiguities/conflicts;
- risks/scenarios;
- existing/generated test references.

Do not collapse these into untyped arrays of strings if that would prevent M1/M2/M3 semantics.

## Manual Test Model design expectations

Even before M3 generation exists, the contract should be compatible with a future manual case containing:

- title/objective;
- provenance/origin;
- environment/build/snapshot;
- actor/profile/permission;
- preconditions;
- parameterized test data;
- ordered step-by-step actions;
- verified path references;
- per-step Expected Result/oracle;
- Pass/Fail/Blocked semantics;
- cleanup/isolation;
- evidence expectations;
- Shared Step/parameter candidates;
- readiness/ambiguity state.

This model must be TMS-neutral.

## Existing-asset preservation expectations

M0 does not implement TMS synchronization, but domain contracts must not force destructive semantics later.

Existing external assets may need stable identity/version/history references. Audit findings and proposed rewrites must be representable separately from the historical asset itself.

Deletion/unlink/history rewrite must not be the default interpretation of a stale/duplicate/obsolete finding.

## Generic-only fixtures

Do not use real customer/project source material as committed eval data. Synthetic fixtures encode the **class of defect**, not a real system.

Generic mutation patterns include numeric constraint changes, required→optional fields, transition addition/removal, permission changes, endpoint contract changes, source deletion, authoritative-source conflict, missing UI path and unspecified retry behavior.

Fixtures should exercise greenfield-compatible and brownfield-compatible model shapes without copying real systems.

## Provider abstraction

If model assistance is introduced, use a typed boundary similar to:

```python
class ReasoningProvider(Protocol):
    def extract(self, request: ExtractionRequest) -> ExtractionResult: ...
    def relate(self, request: RelationRequest) -> RelationResult: ...
    def synthesize(self, request: SynthesisRequest) -> SynthesisResult: ...
```

Every provider result must include provider/model/version metadata when material to reproducibility and must be schema-validated before entering the domain model.

## No premature complexity

Do not add a vector database, GraphRAG, distributed services, autonomous browser execution, Azure/MCP dependency or bulk TMS writes until their milestone and eval evidence justify them.
