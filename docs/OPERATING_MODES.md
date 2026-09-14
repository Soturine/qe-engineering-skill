# Operating Modes

Status: **Normative product behavior**

The system supports different project starting conditions. The engine must adapt its workflow to the available evidence without changing the trust rules.

## Mode A — Greenfield Test Design

Use when project evidence exists but no meaningful manual test plan exists yet.

Typical inputs may include any subset of:

- PRD/product specification;
- functional/non-functional requirements;
- business rules;
- use cases/acceptance criteria;
- ADRs;
- source code and repository history;
- PRs/diffs;
- migrations/data contracts;
- APIs/events/integration contracts;
- UI/design/manual/runbook evidence;
- configuration;
- existing automated tests;
- risk/security/operational policies.

Workflow:

```text
Scope + Source Inventory
        ↓
Source Ledger + Snapshot
        ↓
Project Model
        ↓
Atomic Requirements / Invariants
        ↓
Risk & Scenario Universe
        ↓
Coverage Optimization
        ↓
Manual Test Model
        ↓
Quality Gates
        ↓
Human Review / Approval
        ↓
Preview only by default
        ↓
Optional TMS publication after explicit approval
```

The system may generate a complete manual test plan from zero **only to the level justified by the available evidence**. If code is absent, it may define contractual/manual cases but must not claim implementation alignment. If requirements are absent and only implementation exists, generated cases are characterization/regression unless approved otherwise.

## Mode B — Brownfield / Existing Test Plan Audit

Use when requirements and/or test assets already exist.

The system must inventory and audit before proposing changes. It should evaluate:

- source completeness;
- requirement quality/testability;
- atomic criterion coverage;
- test traceability;
- grouped independent oracles;
- vague/non-executable steps;
- unsupported Expected Results;
- missing preconditions/data/cleanup;
- stale paths/roles/states;
- duplicate or conflicting tests;
- untested negative/boundary/state/security/concurrency/recovery scenarios;
- execution history and recurring failures/blocks;
- opportunities for Shared Steps/parameters;
- missing tests for uncovered behavior/risk.

Default output is an audit + proposed delta. Existing assets remain unchanged until explicitly approved.

## Mode C — Clone / Migration / Reuse Audit

Use when a previous project's test plan or requirement set is cloned as a starting point.

A cloned test is historical input, not truth for the destination project.

Workflow:

```text
Imported/Cloned Assets
        +
Destination Project Evidence
        ↓
Source/Identity Separation
        ↓
Project Model for Destination
        ↓
Compare old assumptions to current evidence
        ↓
Classify each cloned asset
        ↓
Proposed reuse / rewrite / replacement / new coverage
        ↓
Human approval
```

Possible classifications include:

- `REUSABLE`
- `REQUIRES_UPDATE`
- `PARTIAL_COVERAGE`
- `CONFLICTING`
- `DUPLICATE`
- `OBSOLETE_CANDIDATE`
- `UNTRACEABLE`
- `UNKNOWN`

Never copy an old oracle into a new project merely because it existed in the source plan.

## Mode D — Incremental Change / Regression Audit

Use when the project already has a trusted baseline and receives code/PR/requirement changes.

Workflow:

```text
Previous Snapshot + Test Model
            +
New Commit / PR / Requirement Change
            ↓
Change Impact Analysis
            ↓
Affected requirements/entities/states/interfaces/risks
            ↓
Existing TC relevance audit
            ↓
Proposed create/update/re-run set
            ↓
Human approval
```

This mode is a later capability and must preserve the same source/provenance rules.

## Human approval model

Generation and auditing are allowed without external writes. Publication is a separate controlled operation.

Default workflow:

```text
Analyze
→ Generate/Audit
→ Validate
→ Preview/Diff
→ Human Review
→ Explicit Approval
→ Publish/Update/Link
→ Read-back Verification
→ Persist External Mapping
```

No reasoning step implicitly grants publication authority.

Approval should be scoped to the exact proposed operation set and snapshot. If the target changes after preview, approval becomes stale and must be renewed.

## Proposed requirements versus approved requirements

The engine may discover missing decisions or behaviors worth specifying. These are not silently promoted to approved requirements.

Use explicit states such as:

- `PROPOSED_REQUIREMENT`
- `AMBIGUITY`
- `RISK_CONTROL_CANDIDATE`
- `IMPLEMENTATION_ONLY_BEHAVIOR`

Only an authorized human/governance process can promote them into a normative requirement source.

## Read-only default for external systems

External integrations should begin in read/audit mode. Write capability is opt-in and gated.

Recommended capability levels:

1. `READ_ONLY`
2. `AUDIT_ONLY`
3. `PREVIEW_WRITE_PLAN`
4. `APPROVED_WRITE`
5. destructive operations disabled by default

## Success criteria across modes

Regardless of mode, the system must:

- inventory what it used;
- state what it could not read;
- preserve project/snapshot isolation;
- trace normative oracles to primary evidence;
- separate contract, implementation, policy, risk and exploration;
- avoid test-count inflation;
- preserve existing history;
- require human approval before external publication;
- produce operationally executable manual cases when case generation is requested.
