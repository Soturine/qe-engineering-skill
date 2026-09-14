# Manual Test Authoring Contract

Status: **Normative design policy**

## Purpose

Generated manual tests must be executable by a human without oral context and without inventing paths or behavior. The output should resemble a guided checklist suitable for a manual Test Runner while remaining TMS-neutral in the core model.

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
