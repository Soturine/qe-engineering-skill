# Existing Test & Requirement Asset Audit Policy

Status: **Normative design policy**

## Purpose

The system must be safe for both new projects and existing/legacy projects. Existing test cases, requirements, execution results, comments, attachments, screenshots, bug links, audit history and work-item relationships are historical evidence. They must not be destroyed merely because a generated model suggests a different structure.

## Core rule

**Audit before modification. Preserve history by default. Never delete or overwrite historical evidence as part of automated synchronization.**

The system may recommend changes, create replacement/derived assets, append clarifying content or propose deprecation, but destructive operations require an explicit, separately governed workflow outside normal generation/audit mode.

## Existing-asset preservation

Normal operation must not automatically:

- delete an existing Test Case;
- delete or detach an existing requirement/work item;
- delete prior execution results;
- delete comments;
- delete screenshots/attachments/evidence;
- delete linked Bugs/Issues;
- erase historical step results;
- overwrite historical observations;
- remove requirement↔test links solely because a new model disagrees;
- rewrite a previously executed case in a way that destroys the ability to understand what was executed at that time.

## Audit modes

### Brownfield / Legacy Audit

Used when a project already contains requirements, code and/or test assets.

The system should:

1. inventory existing requirements, tests, suites, runs, results, comments, attachments and links;
2. preserve their external IDs and historical relationships;
3. compare them against the current Project Model;
4. classify each asset and finding;
5. propose non-destructive improvements;
6. identify missing tests/coverage;
7. identify stale or contradictory assumptions;
8. identify duplicates without deleting them;
9. identify opportunities for clearer manual steps, preconditions, data, oracles and cleanup;
10. produce a preview/diff before any write.

### Greenfield / New Test Design

Used when project evidence exists but tests do not yet exist, or only partial test assets exist.

The system should:

1. build the Project Model from available evidence;
2. atomize requirements/criteria;
3. map behavior/risk space;
4. generate the smallest defensible manual test set;
5. link generated cases to requirement atoms and risks;
6. publish only after gates and approval.

### Clone / Migration Audit

Used when reusing a previous project/test plan as a starting point.

The system must never assume cloned tests remain correct. It should:

- preserve original identity and provenance;
- compare source project assumptions against the new project snapshot;
- classify each cloned asset as `REUSABLE`, `REQUIRES_UPDATE`, `OBSOLETE_CANDIDATE`, `DUPLICATE`, `CONFLICTING`, or `UNKNOWN`;
- identify project-specific data/path/role assumptions that cannot be reused;
- regenerate links/oracles only from evidence in the destination project;
- never copy a historical oracle into the new project merely because the old project had it.

## Existing Test Case classifications

An existing TC may be classified as:

- `VALID_AS_IS`
- `VALID_WITH_IMPROVEMENT`
- `PARTIAL_COVERAGE`
- `AMBIGUOUS`
- `BLOCKED_BY_SOURCE`
- `DUPLICATE_INTENTIONAL`
- `DUPLICATE_REDUNDANT`
- `CONFLICTING`
- `STALE`
- `OBSOLETE_CANDIDATE`
- `UNTRACEABLE`
- `NON_EXECUTABLE`

Classification alone does not modify the external asset.

## Improvement proposals

Possible non-destructive improvements include:

- add or refine preconditions;
- add explicit manual step-by-step actions;
- split grouped independent validations;
- clarify Expected Results;
- add parameters instead of hard-coded test data;
- suggest Shared Steps for repeated preparation flows;
- add missing requirement/risk links;
- add cleanup/isolation instructions;
- mark ambiguity or missing oracle;
- recommend additional scenarios/tests;
- recommend deprecation or replacement without deleting history.

If an executed TC requires major semantic change, prefer creating a new revision/replacement relationship rather than rewriting historical meaning in place, depending on TMS capabilities.

## Coverage-gap audit

For existing projects, the engine must not stop at `requirement has at least one linked TC`.

It should audit atomic coverage across, when applicable:

- acceptance criteria;
- business rules;
- state transitions and invalid transitions;
- roles/permissions;
- channels/interfaces;
- happy/alternate/negative paths;
- boundaries;
- concurrency;
- retry/idempotency/replay;
- failure/recovery;
- security;
- data integrity;
- time;
- configuration/environment;
- accessibility/operability;
- observability/audit;
- human/physical risks where applicable.

A linked requirement may still have substantial uncovered behavior.

## Comments, screenshots and execution evidence

Historical execution evidence is append-only from the perspective of normal audit/sync behavior.

The system may:

- read it;
- index metadata safely;
- use it as observed operational evidence;
- correlate repeated failures/blocked points;
- propose follow-up actions.

It must not treat comments/screenshots as higher-authority business contract unless explicitly approved, and must not delete them.

## Duplicate handling

Duplicate detection produces a recommendation, not deletion.

Before calling two tests redundant, compare:

- objective;
- oracle;
- requirement atom;
- layer/scope;
- actor;
- state;
- channel;
- test data partition;
- execution history;
- risk covered.

Two similar tests may intentionally cover different layers or regression history.

## Stale/obsolete handling

`OBSOLETE_CANDIDATE` is a review state, not an automatic delete operation.

The system should explain:

- which source changed;
- why the old case may no longer apply;
- whether historical executions must remain accessible;
- replacement candidate, if any;
- migration/traceability links required.

## Write policy

Default adapter capabilities should be ordered from safest to riskiest:

1. read/inventory;
2. audit/report;
3. preview proposed create/update/link operations;
4. create new assets after approval;
5. append non-destructive metadata/comments/links after approval;
6. update unexecuted/current-definition assets after explicit approval and diff review;
7. destructive delete/unlink/history-rewrite: **disabled by default and out of normal generation flow**.

## Idempotency and external identity

Store stable mappings between internal model IDs and TMS/work-item IDs. Re-running an audit must produce a diff, not duplicate everything.

## Audit output

A brownfield audit should produce at least:

- inventory summary;
- source completeness status;
- existing requirement/test traceability matrix;
- atomic coverage gaps;
- duplicate/conflict/stale findings;
- executability/manual-step findings;
- proposed new TCs;
- proposed improvements to existing TCs;
- proposed links/Shared Steps/parameters;
- items requiring human clarification;
- safe publication plan;
- explicit list of operations that will **not** be performed automatically.
