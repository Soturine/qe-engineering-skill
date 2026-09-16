# M4 Product & KISS Addendum

Status: accepted planning addendum for M4. This document does not replace the existing M4 roadmap, trust model, Engineering Constitution, or implementation checkpoints.

## Purpose

M4 is the milestone that turns the M0-M3 evidence/trust engine into a practical, portable Agent Skill for real projects.

The implementation must preserve the existing epistemic core while applying a KISS/product-first rule:

> Ship the simplest useful, defensible v1 that closes the real workflow. Evolve from evidence instead of implementing every possible abstraction up front.

A complete architecture is not the same as a useful first release. Avoid speculative complexity when a smaller design preserves the same trust guarantees.

## Non-negotiable core

Keep the existing direction:

```text
real evidence
  -> deterministic extraction where reliable
  -> bounded heuristics where useful
  -> optional semantic provider where meaning is needed
  -> candidate records
  -> provenance / authority / trust gates
  -> Project Model
  -> QE analysis / Test Model
  -> preview / approval
  -> optional adapter mutation
  -> read-back evidence
```

LLM output is never self-authorizing. Confidence never becomes authority. Implementation never silently becomes contract. External writes remain proposal-first and human-approved.

## Accepted M4 product additions

The following additions are worth implementing because they close real operational gaps rather than adding speculative sophistication.

### 1. Agent runtime state

The production skill should expose an explicit operational lifecycle instead of relying on implicit agent memory.

Suggested high-level states:

```text
DISCOVER
-> SCOPE_ESTABLISHED
-> INVENTORY
-> EVIDENCE_READY
-> UNDERSTAND
-> AUDIT
-> DESIGN
-> GENERATE
-> VALIDATE
-> REVIEW
-> PUBLISH
```

Blocking/review states should be explicit where applicable, for example:

- `BLOCKED_SOURCE`
- `AMBIGUOUS`
- `INVALID_MODEL`
- `STALE_TARGET`
- `APPROVAL_REQUIRED`
- `VALIDATION_FAILED`
- `NOT_VALIDATED`

Do not build a heavyweight workflow engine if a small typed state model is enough.

### 2. QE Run as a first-class artifact

Existing snapshot/run/provenance concepts should converge into a visible reproducible run record.

A run should be able to explain:

- what project/snapshot was analyzed;
- what evidence was studied, partial, blocked, superseded, or out of scope;
- what provider/model/config/prompt version participated;
- what candidates/questions/conflicts were produced;
- what Project Model/Test Model artifacts resulted;
- what validations/reviews/approvals occurred;
- what external operations were previewed/applied/read back.

A practical local workspace may look conceptually like:

```text
.qe/
  runs/
    <run-id>/
      manifest.json
      source-ledger.json
      semantic-candidates.json
      questions.json
      project-model.json
      audit.json
      scenarios.json
      test-model.json
      validation.json
      sync-preview.json
```

The exact file layout is not normative. Prefer the smallest implementation that materially improves reproducibility and debugging.

### 3. Candidate adjudication

Candidate validation alone is insufficient when multiple individually valid pieces of evidence disagree.

Add an explicit relationship/adjudication stage:

```text
candidate set
-> relation analysis
-> agreement / conflict classification
-> adjudication outcome
-> Project Model or review requirement
```

Useful classifications include:

- `CONSISTENT`
- `CONFLICTING`
- `REFINEMENT`
- `SUPERSEDED`
- `DEPLOYMENT_INSTANCE`
- `AMBIGUOUS`
- `HUMAN_DECISION_REQUIRED`

Adjudication does **not** mean the model chooses a winner by itself. A valid outcome is an unresolved conflict that blocks normative promotion.

Source authority may guide interpretation but must not silently erase a divergence. For example, an approved requirement may be more authoritative than source code while the requirement-vs-code mismatch remains a valuable finding.

### 4. Formal question artifacts

Scenario Grilling and ambiguity handling should produce durable question records rather than plain prose only.

A question should be able to carry:

- the question;
- reason/category;
- supporting/conflicting sources;
- whether it is blocking;
- affected requirements/scenarios/Test Models;
- answer provenance when answered;
- reviewer/authority and timestamp where applicable.

The model may generate questions freely. It may not generate unsupported normative answers freely.

### 5. Semantic record distinctions

Where useful, preserve a stronger distinction among concepts such as:

- fact;
- observation;
- claim;
- hypothesis;
- decision;
- oracle.

Do not add duplicate types only for vocabulary. The goal is to prevent an observation or hypothesis from being promoted into a normative oracle by convenience.

### 6. Candidate/provider disagreement handling

M4 does not need multiple live providers.

It should, however, be testable that:

```text
candidate A != candidate B
-> disagreement/conflict
-> review or adjudication
```

High confidence is descriptive metadata and must not resolve disagreement by itself. Fake/static providers are sufficient for M4 contract tests.

### 7. Minimal stale/change propagation

Full change-impact analysis remains M6 work, but M4 needs enough invalidation to support safe
semantic reasoning and reproducible local outputs. Future M5 synchronization consumes these gates.

At minimum:

```text
source hash/snapshot changes
-> dependent semantic candidate/cache becomes stale
-> downstream proposal/Test Model is marked potentially stale where traceability allows
```

Do not build the full M6 dependency/change-impact engine in M4.

### 8. Transactional adapter model (M5, after M6)

Treat external integration as a governed transaction, not as raw CRUD.

Prefer the conceptual lifecycle:

```text
discover
-> snapshot
-> map
-> preview
-> validate target/drift
-> request/verify approval
-> apply
-> read back
-> reconcile
```

Azure DevOps is the first adapter, not the architecture.

### 9. Approval hardening at real write time (M5)

The existing Approval contract already binds important properties such as actor, proposal hash, source/target snapshots, operation set and timestamp.

Do not redesign it unnecessarily.

When real external writes are implemented, evaluate only the missing operational pieces actually needed, such as durable storage, authentication, revocation/expiration semantics, and replay protection.

### 10. Strong run observability

The system should be able to answer:

- Why was this Test Case generated?
- Which evidence/oracle supported it?
- Why was a candidate rejected?
- Which conflict/question blocked readiness?
- What changed between two runs?
- Which adapter operation was approved and what was read back?

Prefer structured artifacts over verbose hidden agent narration.

### 11. Real-world semantic ingestion

M4 must close the gap between "structured evidence -> QE model" and "real project -> structured evidence".

Natural-language project material such as PRDs, ADRs, manuals, validated requirements, use cases, acceptance criteria, backlog text and extracted document text should be able to produce provenance-bound semantic candidates for concepts such as actors, rules, constraints, states and requirements.

Use deterministic parsing first where structure already answers the question. Use semantic reasoning only where meaning actually requires it.

### 12. Semantic mutation evals

Add focused evals that mutate meaning and verify that downstream reasoning reacts.

Examples:

- maximum `100` -> `1000`;
- required -> optional;
- state transition `A -> B` -> `A -> C`;
- role restriction changes;
- superseding requirement changes.

The purpose is to test semantic sensitivity, not just output formatting.

### 13. Oracle quality

Traceable provenance is necessary but not sufficient for a good oracle.

Where practical, validate qualities such as:

- observable;
- sufficiently atomic;
- specific enough to execute;
- measurable/verifiable;
- not vague or circular;
- not an unsupported compound assertion.

Potential findings may include concepts such as `ORACLE_VAGUE`, `ORACLE_COMPOUND`, `ORACLE_NON_OBSERVABLE`, or equivalent existing project terminology.

Avoid adding a complex scoring system unless evals prove it useful.

### 14. Manual executability quality

Extend M3 quality checks only where they improve real manual execution.

Useful checks include:

- vague/implicit action;
- missing actor/state/test data;
- unsupported navigation/path;
- multiple unrelated actions in one step;
- multiple unrelated assertions in one expected result;
- undefined object/status/field;
- non-observable outcome.

Do not mechanically force every step into the same shape if the case is already clear and executable.

### 15. Explainability of coverage

Support the ability to explain both:

- **Why this test exists** — requirement/risk/scenario/oracle/evidence links;
- **Why this was not tested** — e.g. `NOT_APPLICABLE`, `OUT_OF_SCOPE`, `BLOCKED_SOURCE`, `NO_NORMATIVE_ORACLE`, or equivalent project states.

Prefer explicit reasons over misleading single-number coverage claims.

### 16. High-level UX

Keep the advanced commands, but add a simple path for ordinary users.

Target experience:

```text
install
-> qe doctor
-> qe run <project>
```

The user should not need to understand Source Ledger, candidate schemas, oracle validators, M2/M3 internals, or cache identity to get value from the normal path.

`qe run` should orchestrate the existing engine rather than duplicate its trust logic.

### 17. Installation / first-run UX

The normal installation path should be simple and safe.

Desired product characteristics:

- one-command Python CLI installation where packaging allows it;
- safe defaults;
- deterministic-only mode works without external API credentials;
- semantic provider is optional;
- TMS connector is optional;
- clear `qe doctor` diagnostics;
- actionable errors;
- short quickstart;
- no requirement for Azure/MCP/LLM credentials just to use local analysis.

Likely distribution for the Python engine/CLI is PyPI, usable through tools such as `uv tool`, `pipx`, or `pip` as appropriate.

### 18. Agent-runtime neutrality

The engine must not belong to one agent environment.

Conceptually:

```text
                  QE Engine / CLI
                       |
             shared trust authority
                       |
          +------------+------------+
          |            |            |
        Claude       Cursor       Codex/other
        wrapper      wrapper       wrapper
```

The environment is an interface, not the authority.

A thin skill/plugin wrapper should teach an agent when to use the engine, which mode to select, how to react to blocked/review states, and when approval is required. Oracle validity, provenance, source staleness, project isolation and approval validity remain enforced by the engine.

Do not maintain different QE semantics per agent runtime.

### 19. Capability maturity visibility

During M4, expose capability maturity clearly enough to distinguish:

- implemented;
- tested;
- evalled;
- integrated;
- production-ready.

A compact `M4_STATUS` capability matrix is acceptable if it reduces ambiguity. Avoid duplicating status across many documents.

## KISS guardrails

The following are explicitly **not** reasons to delay a useful M4 v1 unless concrete evidence shows they are required:

- GraphRAG;
- vector database;
- autonomous browser;
- multi-agent swarm;
- many live semantic providers;
- massive MCP integration;
- distributed architecture;
- full M6 change-impact graph;
- full call/dataflow graph;
- splitting the Python core into multiple services;
- OS-level parser sandbox as a universal M4 completion gate.

This does not mean these ideas are forbidden forever. They require evidence that the simpler design is insufficient.

## Implementation sequencing relative to current H2

Do not restart or discard valid M4.H2 work to implement this addendum.

The current sequence remains checkpoint-driven:

```text
finish current checkpoint
-> targeted validation
-> logical commit
-> push
-> CI / last-known-green
-> next checkpoint
```

Integrate the additions at the smallest natural checkpoint after H2. Avoid a single large refactor merely to make the architecture look complete.

Suggested fit with the existing M4 sequence:

- H2: finish provenance-bound candidates/cache identity as already designed;
- H3-H5: semantic distinctions, relation/adjudication, real-world ingestion, stale propagation;
- H6: formal question artifacts / Scenario Grilling integration;
- H7: oracle/executability wording gates where appropriate;
- D1 after H4: offline PT-BR Technical Preview UX and demo; freeze before H5;
- H8: local orchestration/output/export; transactional adapters move to M5 after M6;
- H9: runtime state, `qe run`, `qe doctor`, portable production skill/agent wrappers, capability maturity;
- H10: semantic mutation, disagreement, run/workspace, end-to-end synthetic evals;
- H11: simplify, remove accidental complexity, validate packaging/first-run flow, harden docs.

The exact allocation may change if implementation evidence shows a simpler fit.

## M6 audit carry-forward

When the whole-system audit begins, prioritize the flagship milestones M0, M3, M4 and M6 while still checking M1/M2/M5 boundaries.

Preferred audit sequence:

```text
Astra Light broad audit
-> reproduce/confirm plausible findings
-> Astra Light fixes
-> targeted + full validation
-> Astra Light recheck
-> Astra Medium deep audit of surviving/high-risk findings
-> Medium fixes
-> final full-system validation / benchmark regression
```

A model finding is not a confirmed defect. Preserve the engineering evidence lifecycle:

```text
finding
-> reproduce
-> failing test/eval
-> fix
-> targeted validation
-> full suite
-> benchmark regression
```

Focus especially on M0<->M4 trust boundaries, M3 oracle/path correctness, M4 semantic/adjudication/integration behavior, and M6 benchmark/audit integrity.

## Product positioning

The project should not optimize around the commodity claim "AI that generates test cases."

The stronger positioning is:

> **Evidence-first Quality Engineering runtime for AI agents.**

A useful shorthand is:

```text
Agent reasons.
Engine establishes what is defensible.
Human governs high-consequence decisions.
Adapter executes only approved operations.
```

## M4 product exit intent

A strong M4 v1 should make this possible without requiring the user to understand the internal architecture:

```text
install
-> point at a real project
-> ask for QE work in natural language or run `qe run`
-> inventory evidence
-> understand supported semantics
-> surface conflicts/questions
-> audit/design/generate
-> validate
-> local PT-BR HTML/Markdown/JSON review
-> preserve conflicts/questions and evidence
```

The internal architecture may be sophisticated. The normal user experience should not be.

`ROADMAP.md` owns the revised execution order M4 → M6 → M5. External preview/approval/sync/
read-back remains a binding future M5 safety contract, not a M4 exit requirement.
