# Manual Test Authoring Contract

Status: **Normative design policy**

## Purpose

Generated manual tests must be executable by a human without oral context and without inventing paths or behavior. The output should resemble a guided checklist suitable for a manual Test Runner while remaining TMS-neutral in the core model.

This contract applies in every operating mode:

- generating a plan from zero;
- improving an existing Test Case;
- auditing a legacy plan;
- reusing/cloning tests into another project;
- generating new coverage discovered during an audit;
- preparing regression cases after change-impact analysis.

The engine must be able to produce the proposed manual Test Model **without any Azure DevOps, Jira, TestRail, MCP or other TMS connection**. TMS integrations are optional read/write adapters, not prerequisites for analysis or authoring.

## Canonical manual test structure

Each generated manual test should contain, when applicable:

- stable internal test ID;
- title;
- objective;
- origin (`CONTRACT`, `IMPLEMENTATION`, `ORGANIZATIONAL_POLICY`, `RISK`, `EXPLORATORY`);
- primary source/provenance links;
- related requirement atoms / risks;
- priority/severity/risk rationale;
- environment/build/snapshot assumptions;
- actor/profile/permission requirements;
- preconditions;
- test-data properties/parameters;
- ordered manual steps;
- per-step Expected Result when there is an observable oracle;
- Pass/Fail/Blocked semantics;
- cleanup/isolation;
- evidence expectations;
- ambiguity/blocking notes;
- candidate Shared Steps / Shared Parameters;
- readiness state.

## Step contract

A manual step should answer as much as needed of:

- **Where**: verified screen/module/API/tool/location;
- **Who**: actor/profile when relevant;
- **Preparation**: required state/data;
- **Action**: exact human action;
- **Expected Result**: directly observable outcome with oracle provenance;
- **Failure note**: what contradiction would fail this validation, when helpful.

Do not overload one step with unrelated oracles. Independent validations should be separate steps or separate tests when that improves diagnosability.

## Guided step-by-step output

The system should generate the operational step-by-step itself; this is not merely a formatting adapter concern.

Example shape (generic only):

```text
Preconditions
- User with required permission exists.
- Record satisfying data condition A exists.

Step 1 — Open target capability
Action:
Navigate through the verified path to the target capability.

Expected:
The capability is available to the authorized actor.

Step 2 — Perform the business action
Action:
Enter the prepared parameterized data and submit.

Expected:
The observable state changes according to the source-backed oracle.

Step 3 — Validate negative boundary
Action:
Repeat using the defined invalid/boundary data partition.

Expected:
The operation is rejected or handled according to the source-backed oracle.
```

The actual generated text must use the names/paths/data discovered in the analyzed project. Generic placeholders are only for synthetic fixtures and documentation.

## Verified-path rule

A path such as `Menu → Module → Screen → Action` may be generated only when supported by current evidence such as UI/runtime observation, approved manual/design, route/template code, or equivalent proof.

If a path is not confirmed:

- do not invent it;
- keep the test `READY_WITH_REVIEW`, `AMBIGUOUS` or `BLOCKED_SOURCE` as applicable;
- state what path evidence is missing.

## Preconditions versus Shared Steps

Preconditions describe required state. Shared Steps describe reusable executable preparation sequences.

The engine may propose a Shared Step when a repeated sequence is:

- stable;
- genuinely reused;
- not the core validation/oracle of the test;
- still understandable when referenced.

Execution result of a Shared Step in one TC does **not** automatically mark it passed in other TCs.

## Test data

Prefer properties and parameters over fixed IDs:

- `existing active user with role X`;
- `record at lower boundary`;
- `unique valid identifier`;
- `resource owned by a different tenant/account`.

Hard-coded IDs are allowed only when the environment/test contract explicitly requires them.

## Evidence burden

A normal low-risk Pass should be lightweight. Screenshots/log attachments are not required for every step unless policy/audit risk requires them.

For Fail/Blocked/high-risk controls, capture enough observed information to diagnose and reproduce the deviation.

## Overall result

When one TC contains multiple required validation steps, overall Pass requires all required steps to satisfy their oracles. A failure should identify the exact failed validation.

## Gherkin / INVEST / 5W2H

These are design aids, not mandatory output syntax.

- Gherkin may help normalize scenario logic.
- INVEST may help assess requirement/testability quality.
- 5W2H may help ensure operational context is complete.

The final manual output remains action-oriented and human-executable.

## Existing test enhancement

For existing TCs, the engine may propose this structure as a non-destructive revision. It must preserve historical executions and use the Existing Asset Audit Policy before any update.

A brownfield audit may therefore produce:

- the original TC as-is;
- a proposed step-by-step rewrite;
- a field-level/step-level diff;
- rationale for each proposed change;
- new TCs for uncovered scenarios kept separate from revisions to existing TCs.

No proposed rewrite is applied automatically.

## Clone/reuse behavior

When a Test Plan or Test Case is cloned/reused for another project, the step-by-step must be regenerated or revalidated against the **destination project's** evidence.

Do not blindly carry over:

- UI paths;
- roles/permissions;
- field names;
- statuses/states;
- messages;
- identifiers;
- workflow ordering;
- test data;
- Expected Results;
- cleanup behavior.

A cloned case may preserve its conceptual objective while receiving a different operational procedure when the destination evidence supports it. If destination evidence does not support the old oracle, classify the case accordingly rather than preserving it by inertia.

## Tool independence

Manual Test Models must remain useful as standalone structured artifacts and be renderable to Markdown/JSON/YAML or another local output even when no external TMS connector is available.

The following capabilities must not depend on Azure DevOps MCP or any other external TMS connector:

- source inventory;
- Project Model construction;
- requirements/rules audit;
- existing TC audit from exported/local artifacts;
- scenario/risk analysis;
- coverage-gap analysis;
- generation of new TCs;
- generation of proposed step-by-step improvements;
- quality-gate validation;
- preview/diff rendering.

A TMS connector only adds live inventory, live history and publication/synchronization capabilities.

## Human approval

Generation is a proposal. Auditing is a proposal. Rewriting is a proposal. Publication is a separate controlled operation.

No generated/improved Test Case, requirement, Shared Step, link, comment, attachment or status change may be written to an external system merely because the engine/model produced it.

Human approval must be explicit, scoped to the exact proposal and source/target snapshot, and becomes stale if the target changes before application.
