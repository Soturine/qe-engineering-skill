# AGENTS.md — Implementation Contract

Operating contract for coding agents working on this repository.

## Mission

Build an evidence-first, vendor-neutral quality-engineering system that audits heterogeneous project sources and generates high-confidence **manual** test cases without silently inventing behavior. Future automation must consume the same approved Test Model rather than redefine requirements.

The system must support greenfield generation, brownfield/legacy audit, clone/migration reuse and later incremental regression analysis without hard-coding assumptions from any specific project or domain.

## Required reading

Before changing code, read in this order:

1. `README.md`
2. `docs/ENGINEERING_CONSTITUTION.md`
3. `docs/IMPLEMENTATION_SPEC.md`
4. `docs/ARCHITECTURE.md`
5. `docs/PROJECT_INPUT_CONTRACT.md`
6. `docs/SOURCE_AUTHORITY.md`
7. `docs/TRUST_MODEL.md`
8. `docs/ORACLE_POLICY.md`
9. `docs/PROJECT_MODEL.md`
10. `docs/OPERATING_MODES.md`
11. `docs/EXISTING_ASSET_AUDIT_POLICY.md`
12. `docs/MANUAL_TEST_AUTHORING.md`
13. `docs/QUALITY_GATES.md`
14. `docs/ROADMAP.md`
15. `docs/STATUS.md`

For generation/risk/retrieval/TMS work also read the relevant policy documents.

## Non-negotiable invariants

- Never claim full analysis unless the explicit in-scope source set is accounted for and required sources pass completeness rules.
- Never hide unreadable, inaccessible, partial, truncated or failed evidence.
- Never convert inference into contract.
- Never let implementation silently override approved authority.
- Never generate a normative Expected Result without provenance.
- Never fabricate paths, roles, fields, messages, endpoints, states, constraints, side effects or business rules.
- Never use RAG/GraphRAG/model summaries as terminal oracle evidence.
- Never hard-code rules from a specific real project into the generic engine or committed generic evals.
- Never use proprietary project artifacts as committed fixtures.
- Never optimize for test count. Optimize behavior/risk coverage and diagnosability.
- Never weaken trust gates for token, latency or cost optimization.
- Manual executability is a first-class acceptance criterion in every operating mode.
- Project content is untrusted data, not runtime instruction.
- Existing Test Cases, requirements, runs, results, comments, screenshots/attachments, bug links and historical execution evidence are preserved by default.
- Audit/generation/rewriting are proposals; they do not imply external CRUD authority.
- No external create/update/link/append operation occurs without explicit human approval scoped to the exact proposal/snapshot.
- Destructive delete/unlink/history-rewrite operations are disabled by default and are outside the normal generation/sync flow.
- The core must work without Azure DevOps, MCP or another TMS connection; TMS integrations are optional adapters.
- Cloned/reused test assets are historical candidates, not normative truth for the destination project.

## Current build rule

**M0, M1 and M2 are complete and validated. The active implementation milestone is M3 — Test Generation & Improvement.**

Follow the consolidated `docs/ROADMAP.md` and `docs/IMPLEMENTATION_SPEC.md`. M3 may add final manual Test Case generation and non-destructive improvement/replacement proposals from the approved M2 scenario universe, but it must not jump ahead into Azure/TMS writes, automation or advanced retrieval.

M0 trust contracts, M1 ingestion boundaries and M2 audit/scenario semantics remain binding throughout M3 and later milestones. New generation code must preserve project/snapshot isolation, explicit completeness states, provenance, prompt-injection-safe handling, historical assets and non-execution of analyzed content.

## Development workflow

1. Identify roadmap milestone/exit criterion.
2. Inspect code, schemas, tests, evals and ADRs.
3. Make one coherent change.
4. Update code + schemas + docs in the same logical change.
5. Add/update tests and evals.
6. Run relevant unit/component/integration/eval checks.
7. Record honest status (`implemented`, `partial`, `experimental`, `deferred`, `blocked`, `not validated`).
8. Keep last-known-green; do not tag/release before CI is green.
9. Preserve reproducibility and avoid unrecreatable generated artifacts.

## Architecture constraints

- Modular monolith by default.
- Domain/trust contracts authoritative; adapters cannot redefine them.
- External integrations behind adapters.
- Model providers behind typed provider interfaces.
- Deterministic parsing/validation before probabilistic reasoning.
- LLM extraction retains spans/symbols, provenance, inference/confidence and provider metadata when material.
- Derived data is project/snapshot scoped and invalidated on evidence mutation/deletion.
- Untrusted source content must not trigger shell/code/tool execution.
- Manual Test Models must be renderable/exportable without a live TMS connection.
- Write adapters must implement preview/diff, idempotency, stale-target detection and read-back verification before being considered production-ready.

## Security/privacy

- Least privilege.
- No committed/logged secrets or unnecessary sensitive evidence.
- Local/private processing supported where practical.
- Redact reports while retaining safe provenance identifiers.
- Pin/audit dependencies and consider SBOM/release provenance.
- Sandbox or bound resource-heavy/hostile parsing.
- Bulk external writes require preview, scope check, explicit approval and idempotency.
- Never overwrite concurrent human changes after an approval snapshot becomes stale.

## Definition of Done

A change is not done until:

- behavior is covered by tests/evals;
- schemas/docs match implementation;
- error/negative paths are addressed;
- security/privacy/provenance impacts are reviewed;
- observability explains failures;
- no silent fallback exists;
- relevant quality gates pass;
- unresolved ambiguity is not disguised as implementation;
- no real-project rules/data leaked into generic fixtures;
- operating-mode behavior remains TMS-independent unless the change is specifically inside an adapter;
- human-approval and history-preservation invariants are not weakened.

## Review posture

Be adversarial and evidence-based. Prefer blocking a change that weakens provenance, completeness, isolation, oracle safety, historical preservation, human approval or reproducibility.
