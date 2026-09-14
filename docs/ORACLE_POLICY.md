# Oracle Policy

## Definition

A test oracle is the basis for deciding whether observed behavior is correct. Every normative Expected Result must have a defensible oracle.

## Allowed oracle origins

### CONTRACT

Approved requirement, business rule, use case, acceptance criterion, protocol, regulation or equivalent source.

### IMPLEMENTATION

Observed/confirmed implementation may define characterization/regression expectations when explicitly labeled. It must not silently become a business requirement.

### ORGANIZATIONAL_POLICY

Explicit security, quality, privacy or engineering policy may define expected controls within its scope.

### RISK

A risk-derived scenario can become normative only when a safe invariant can be justified (for example, cross-tenant data must not be exposed) or after human approval. Otherwise it remains review/exploratory.

### EXPLORATORY

No Pass/Fail oracle. The output is a charter, question or observation objective.

## Forbidden behavior

The generator must not invent:

- UI menus or paths;
- exact messages not specified/observed;
- roles or permissions;
- state transitions;
- rollback semantics;
- endpoint behavior;
- field aliases;
- timing guarantees;
- error codes;
- data constraints;
- side effects;
- cleanup behavior.

## Oracle record

A normative oracle should contain:

```yaml
statement: "..."
origin: CONTRACT
sources:
  - source_id: REQ-001
    location: "RN-003"
inferred: false
confidence: high
```

If `inferred: true`, a normative output requires an explicit approval record or a policy-backed invariant.

## Ambiguity behavior

If a result cannot be defended, create an ambiguity record with:

- missing decision;
- affected scenarios/tests;
- conflicting/insufficient sources;
- proposed question;
- risk of guessing.

Do not fill the gap with “reasonable” behavior.

## Observed implementation versus contract

When contract and implementation disagree, preserve both claims and create a divergence finding. The current implementation may be used for characterization testing while the contractual case remains failed or blocked according to execution context; the engine must not erase either view.
