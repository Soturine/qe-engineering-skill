# Azure DevOps Test Plans Adapter

Status: **Future adapter contract**

## Boundary

Azure DevOps is a renderer/integration target, not the domain model. The core Test Model remains TMS-neutral.

The adapter must support both **greenfield generation** and **brownfield/legacy audit**. Existing test assets and execution history are evidence and must be preserved by default.

See `EXISTING_ASSET_AUDIT_POLICY.md`.

## Safety principle

**Read/audit/preview first; create/update only after approval; destructive operations are disabled by default.**

Normal operation must not automatically delete or erase:

- Test Cases;
- requirements/work items;
- test runs/results;
- comments;
- screenshots/attachments;
- bug links;
- historical step results;
- requirement↔test traceability;
- execution evidence.

If an artifact appears stale, duplicated or obsolete, the adapter creates a finding/proposal. It does not delete history.

## Operating modes

### Audit-only

Read existing plans/suites/cases/runs/results/comments/attachments/links and produce findings. No writes.

### Preview/dry-run

Render a sync plan showing proposed `CREATE`, `UPDATE`, `LINK`, `APPEND`, `NOOP`, `REVIEW`, and `SKIP` operations without applying them.

### Approved sync

Apply only explicitly approved non-destructive operations. Every applied change must be verified after write and recorded in the mapping ledger.

### Destructive maintenance

Deletion, unlinking, evidence removal or history rewriting is outside normal generation/sync flow and disabled by default. If ever supported, it requires a separate capability, explicit high-friction approval and dedicated audit log.

## Manual Test Case mapping

The adapter should map approved structured cases to native concepts such as title, preconditions/description where supported, Action + Expected Result steps, parameters/shared parameters where suitable, requirement/work-item links, tags/priority/custom fields through configuration, and Shared Steps suggestions for genuinely reusable sequences.

Do not invent runner controls or per-step states that the target TMS does not support.

## Existing Test Case audit

Before proposing an update to an existing case, preserve and inspect:

- external work-item ID;
- current definition/version metadata where available;
- linked requirements/suites;
- execution history;
- comments;
- screenshots/attachments/evidence references;
- linked Bugs/Issues;
- previous outcomes;
- existing Shared Steps/parameters.

Classify the case using the existing-asset audit policy before modification.

For a case with execution history, semantic rewrites require extra caution. Prefer a new revision/replacement relationship when changing the meaning of what was historically executed.

## Shared Steps policy

Suggest Shared Steps when a sequence is repeated across several cases, operationally stable, a preparation/common workflow rather than the unique oracle under test, and still understandable when referenced.

Do not hide the essential validation of a test inside a shared step merely to deduplicate text.

Shared Steps reuse definitions; they do not imply that execution results automatically carry across independent Test Cases.

## Parameters

Use parameters for data variants that preserve the same workflow/oracle structure. Materially different workflows remain separate cases.

## Requirement/work-item handling

Existing requirements are audited and linked rather than recreated blindly.

A missing requirement candidate discovered by risk analysis or source inconsistency must not be silently published as an approved business requirement. It should remain a proposed finding/draft until governed approval establishes authority.

The adapter must support configurable mapping for the process used by the Azure project rather than hard-coding a single work-item type.

## Publication safety

Before writing:

1. validate case/readiness and schema;
2. resolve target organization/project/plan/suite/process configuration;
3. refresh external state to detect drift since audit;
4. render a preview/diff;
5. validate field/length/workflow mappings;
6. verify that proposed updates preserve historical evidence;
7. require explicit approval for bulk create/update/link/append operations;
8. use idempotency keys/mapping records to avoid duplicate publication;
9. write using least privilege;
10. read back and verify the resulting external artifact;
11. log external IDs, operations and outcomes.

## Idempotency and mapping ledger

Maintain a stable mapping such as:

`internal_artifact_id + project/snapshot scope ↔ Azure external ID`

A subsequent run must compare desired/current state and produce `NOOP` when unchanged. Re-running the engine must not duplicate existing cases or links.

Mapping must not rely only on title matching.

## Optimistic concurrency / drift

Between audit and write, an external asset may change. The adapter must re-read relevant state before mutation and reject/review stale writes rather than overwrite concurrent human changes.

## Execution feedback

Ingestion should preserve case/run/result identity, Pass/Fail/Blocked semantics, step results where available, comments/evidence references, bug/work-item links and execution timestamp/environment/build/snapshot.

Execution evidence updates knowledge only as observed operational evidence unless explicitly promoted through a governed decision.

Comments and attachments are append-only historical evidence from the perspective of ordinary sync: ingest/reference them, never erase them.

## Brownfield audit outputs

For an existing Azure Test Plan, support generation of:

- inventory and source completeness report;
- requirement↔TC traceability;
- atomic coverage gaps;
- tests without defensible oracle/source;
- unclear/non-executable steps;
- missing preconditions/data/cleanup;
- duplicate, conflicting, stale and obsolete-candidate findings;
- missing Shared Step/parameter opportunities;
- proposed new tests for uncovered behavior/risk;
- proposed non-destructive improvements;
- safe sync diff requiring human approval.

## Clone/migration use

When a Test Plan or project is cloned/reused, treat the imported tests as historical candidates, not truth. Revalidate each case against the destination project's evidence before reusing its oracle, paths, actors, data or requirement links.
