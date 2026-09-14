# Azure DevOps Test Plans Adapter

Status: **Future adapter contract**

## Boundary

Azure DevOps is a renderer/integration target, not the domain model. The core Test Model remains TMS-neutral.

## Manual Test Case mapping

The adapter should map approved structured cases to native concepts such as title, preconditions/description where supported, Action + Expected Result steps, parameters/shared parameters where suitable, requirement/work-item links, tags/priority/custom fields through configuration, and Shared Steps suggestions for genuinely reusable sequences.

Do not invent runner controls or per-step states that the target TMS does not support.

## Shared Steps policy

Suggest Shared Steps when a sequence is repeated across several cases, operationally stable, a preparation/common workflow rather than the unique oracle under test, and still understandable when referenced.

Do not hide the essential validation of a test inside a shared step merely to deduplicate text.

## Parameters

Use parameters for data variants that preserve the same workflow/oracle structure. Materially different workflows remain separate cases.

## Publication safety

Before writing:

1. validate case readiness and schema;
2. resolve target project/plan/suite/configuration;
3. render a preview/diff;
4. validate field/length/workflow mappings;
5. require explicit approval for bulk create/update;
6. use idempotency keys/mapping records to avoid duplicate publication;
7. log external IDs and result.

## Execution feedback

Future ingestion should preserve case/run/result identity, Pass/Fail/Blocked semantics, step results where available, comments/evidence references, bug/work-item links and execution timestamp/environment/build/snapshot.

Execution evidence updates knowledge only as observed operational evidence unless explicitly promoted through a governed decision.
