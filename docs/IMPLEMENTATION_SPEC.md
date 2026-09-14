# Implementation Specification for Coding Agents

Status: **Build plan**

This document exists so a coding agent can implement the repository without relying on conversation history or a specific example project.

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

## M0 implementation order

1. Establish package/tooling and CI.
2. Implement typed domain objects or validated mappings for Run Manifest, Source Ledger, Claim/Provenance, Oracle, Risk, Test Case and a Project Model skeleton.
3. Add JSON Schema validation.
4. Add cross-field policy validators that schemas cannot express safely.
5. Implement hard gates:
   - reject normative oracle without provenance;
   - reject normative inferred oracle without allowed approval/policy path;
   - reject `COMPLETE` when a required source is incomplete;
   - reject invalid project/snapshot isolation.
6. Create synthetic fixtures and adversarial tests.
7. Add structured error/result types; do not use exceptions as the only user-facing diagnosis.
8. Add CLI only when it exercises real validators, for example `qe validate-ledger`, `qe validate-oracle`, `qe validate-test-case`.
9. Keep Agent Skill scaffold thin until M0 exit criteria are executable.
10. Update docs/status honestly.

## M0 exit criteria

M0 is complete only when automated tests prove:

- unsupported normative oracles are rejected;
- incomplete required sources prevent `COMPLETE`;
- inference cannot silently become contract;
- project/snapshot IDs are enforced;
- validation errors identify the violated rule and artifact;
- schemas and validators are versioned;
- synthetic eval policy is followed;
- no live model is required to test deterministic core behavior.

## Generic-only fixtures

Do not use real customer/project source material as committed eval data. Synthetic fixtures encode the **class of defect**, not a real system.

Generic mutation patterns include numeric constraint changes, required→optional fields, transition addition/removal, permission changes, endpoint contract changes, source deletion, authoritative-source conflict, missing UI path and unspecified retry behavior.

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

Do not add a vector database, GraphRAG, distributed services, autonomous browser execution or bulk TMS writes until their milestone and eval evidence justify them.
