# Codex Task — Implement M0 Foundations & Trust Model

Use this document as the first implementation handoff. It is intentionally generic and does not depend on any real project dataset.

## Objective

Implement **M0 — Foundations & Trust Model** from `ROADMAP.md` so the repository can mechanically reject unsupported normative test oracles, false completeness claims and cross-project/snapshot contamination before any production test-case generator is built.

The implementation should be **lean but structurally sound**: build the critical trust core first, avoid premature complexity, and leave clear extension points for M1/M2.

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
- `STATUS.md`

Do not rely on conversation history. The repository is the source of implementation intent.

## Implementation posture

- Prefer Python with typed models and deterministic validators.
- Prefer a modular monolith/package.
- Keep dependencies minimal and justified.
- No live LLM is needed for M0.
- Do not implement a production test-case generator yet.
- Do not add RAG, GraphRAG, vector databases or autonomous browser execution.
- Do not couple domain logic to Claude/OpenAI/Copilot.
- Do not use real proprietary/customer/project artifacts as committed fixtures.
- If an adjacent M1/M2 foundation is necessary to avoid a poor or destructive M0 design, implement the **smallest necessary subset** and document why. Do not broadly jump milestones.

## Required deliverables

Implement a Python package and CI-ready test suite containing:

1. **Versioned JSON Schemas** for at least:
   - Run Manifest;
   - Source Ledger;
   - Claim/Provenance;
   - Oracle;
   - Approval;
   - Risk;
   - Project Model skeleton;
   - Test Case/Test Model skeleton.

2. **Typed domain objects** or equivalent strongly validated structures for the same concepts.

3. **Project Model skeleton with future-proof semantics**. It does not need full extraction yet, but it must support representative generic nodes and relationships from `PROJECT_MODEL.md`, including at least:
   - Entity;
   - Field/Constraint;
   - Actor/Role/Group mapping;
   - Permission;
   - State;
   - Transition;
   - Channel;
   - Action/Event;
   - Interface/Integration;
   - Requirement + atomic criterion;
   - Invariant;
   - Ambiguity/Conflict;
   - Risk/Scenario;
   - Existing/generated Test reference;
   - provenance-bearing IDs and project/snapshot namespace.

   Do **not** hard-code any domain names, statuses, actors, channels or business rules.

4. **Deterministic cross-artifact validators** for:
   - normative oracle provenance;
   - inference/approval rules;
   - completeness versus source study/read states;
   - source authority constraints where mechanically decidable;
   - project/snapshot isolation;
   - valid readiness transitions;
   - verified-path claims requiring evidence;
   - references to missing semantic nodes;
   - unsupported cross-snapshot links.

5. **Structured validation errors** with stable codes, severity and artifact references. Examples of error-code families:
   - `SRC_*`
   - `ORACLE_*`
   - `PROV_*`
   - `MODEL_*`
   - `SCOPE_*`
   - `READY_*`
   - `APPROVAL_*`

6. **Minimal CLI** that exercises real validators, for example:
   - `qe validate-ledger <file>`
   - `qe validate-oracle <file>`
   - `qe validate-project-model <file>`
   - `qe validate-test-case <file>`

7. **Synthetic generic fixtures** and automated tests for hard trust invariants.

8. **Basic CI** that runs the chosen formatting/lint/type checks plus unit/eval tests.

9. **Status/docs update** reflecting exactly what is implemented, partial, deferred or unvalidated.

## Required negative tests

At minimum prove that the implementation rejects or downgrades correctly:

- a normative Expected Result with no source/provenance chain;
- an inferred normative oracle with no allowed approval/policy path;
- `COMPLETE` when a required source is `BLOCKED`, `NOT_STUDIED`, `PARTIALLY_STUDIED`, `TRUNCATED`, `FAILED` or `UNVERIFIED` as applicable;
- a source/claim/test/model artifact referencing another project/snapshot namespace without explicit allowed linkage;
- an approval record missing attribution, scope or approved artifact;
- a verified UI/API/CLI/physical path with no supporting evidence;
- a semantic reference to a missing node;
- an implementation-origin claim silently relabeled as contract;
- duplicate IDs within the same namespace;
- invalid readiness promotion when a blocking conflict exists.

Also prove that valid minimal fixtures pass.

## Representative generic fixture expectations

Use synthetic domains only. Include at least one fixture with:

- two entities and one relationship;
- one actor, one role and one permission mapping;
- a three-state state machine;
- one normal and one exception transition;
- two different channels;
- one API/interface contract;
- one atomic requirement criterion;
- one risk-derived scenario;
- one ambiguity or conflict;
- one valid normative oracle;
- one rejected unsupported oracle;
- one manual Test Model referencing verified path/provenance.

The names must be generic/synthetic and must not reproduce a real project.

## Quality expectations

- Schema validation is not enough: implement cross-field/domain validators for invariants JSON Schema cannot safely enforce.
- Confidence must never substitute for authority.
- `inferred=true` must remain visible end-to-end.
- Source deletion/supersession behavior should be considered in model design even if full invalidation is deferred.
- No silent fallback from a failed source to stale or unrelated evidence.
- Error messages must be diagnosable by a human or another agent.
- Tests should verify properties and invariants, not brittle prose formatting.

## Git workflow for this task

For now, work **directly on `main`**.

Use small, logical commits and push each coherent green checkpoint. Suggested sequence:

1. `chore: bootstrap python package and quality tooling`
2. `feat: add versioned trust schemas and domain models`
3. `feat: implement provenance and completeness validators`
4. `feat: add project model skeleton and integrity validation`
5. `test: add adversarial trust fixtures and evals`
6. `ci: add quality and test workflow`
7. `docs: update implementation status and m0 evidence`

Rules:

- do not squash unrelated work into one giant commit;
- run relevant tests before each push;
- keep `HEAD == origin/main` after every push;
- if a checkpoint is red, fix it before advancing;
- do not create a release/tag during M0 unless explicitly requested;
- do not auto-merge anything;
- report commit SHA for each checkpoint in the completion summary.

## Stop conditions

Stop and report instead of guessing if:

- normative docs conflict in a way that changes the trust model;
- a requested invariant cannot be implemented without changing the architecture materially;
- the chosen schema shape would make M1/M2 semantics impossible;
- a dependency introduces disproportionate supply-chain or licensing risk;
- CI cannot be made green without weakening a gate.

## Completion report

When finished, report:

- files added/changed;
- architecture decisions made;
- commands/tests executed;
- exact M0 exit criteria satisfied;
- any small M1/M2 foundations implemented early and why;
- remaining gaps/deferred work;
- security/provenance tradeoffs;
- commit SHAs in order;
- current `HEAD` and `origin/main`;
- CI status.

Do not mark M0 complete if any hard invariant is untested or failing.
