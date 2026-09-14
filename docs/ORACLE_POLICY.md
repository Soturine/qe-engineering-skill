# Oracle Policy

## Definition

A test oracle is the basis for deciding whether observed behavior is correct. Every normative Expected Result must have a defensible oracle.

## Allowed oracle origins

### CONTRACT
Approved requirement, business rule, use case, acceptance criterion, protocol, regulation or equivalent authority.

### IMPLEMENTATION
Observed/confirmed implementation may define characterization/regression expectations when explicitly labeled. It must not silently become a business requirement.

### ORGANIZATIONAL_POLICY
Explicit security, quality, privacy or engineering policy may define expected controls within its scope.

### RISK
A risk-derived scenario can become normative only when a safe invariant is justified by policy/authority or after explicit governed human approval. Otherwise it remains review/exploratory.

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

A normative oracle should contain at least:

```yaml
statement: "The value must satisfy the approved constraint"
origin: CONTRACT
sources:
  - source_id: REQ-042
    location: "acceptance criterion 2"
inferred: false
confidence: high
approval: null
```

If `inferred: true`, normative output requires an explicit approval record or policy-backed invariant. Approval itself is provenance and must include actor/authority, scope, timestamp, decision and reason.

## Source chain

A publishable normative oracle must support:

`Expected Result → oracle → claim(s) → primary source location(s) → authority decision`

A model summary, embedding match or GraphRAG claim can help find evidence but cannot terminate this chain.

## Ambiguity behavior

If a result cannot be defended, create an ambiguity record with missing decision, affected scenarios/tests, conflicting/insufficient sources, proposed question and risk of guessing.

Do not fill the gap with “reasonable” behavior.

## Observed implementation versus contract

When contract and implementation disagree, preserve both claims and create a divergence finding. Current implementation may be used for explicitly labeled characterization testing while contractual behavior remains separate; the engine must not erase either view.

## Invalidated evidence

If supporting evidence is deleted, superseded, becomes unreadable or changes materially, dependent oracles must be revalidated, downgraded or invalidated. Cached derivations may not keep an oracle alive after its support disappears.
