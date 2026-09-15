# Normalized Project Model

Status: **Normative target intermediate representation**

## Purpose

The Project Model separates project understanding from test generation. Agents must first build and validate a normalized, evidence-backed model; they must not generate normative test cases directly from arbitrary retrieved chunks.

The model is generic. Domain-specific names, states, roles, channels and rules are discovered from project evidence and must never be hard-coded into the engine.

## Design goals

The Project Model must be able to reconstruct, when applicable:

- what the system is made of;
- who can act;
- what actions/events exist;
- which states and transitions exist;
- which channels/interfaces can trigger behavior;
- which constraints, guards and invariants apply;
- which side effects/integrations occur;
- which source proves each claim;
- where sources disagree or remain incomplete;
- which atomic behaviors are tested or untested;
- which risk-derived scenarios exist beyond explicit requirements.

## Required top-level sections

A mature Project Model should represent, when applicable:

- run/snapshot identity;
- Source Ledger;
- extracted claims and source spans/symbols;
- requirements and atomic requirement criteria;
- entities, fields, relationships and constraints;
- actors, roles, groups and permissions;
- states, transitions, guards, exceptions and channels;
- actions, commands, events and workflows;
- verified UI/API/CLI/physical interaction paths;
- APIs, events, queues, files and integration contracts;
- persistence and migration constraints;
- timings, limits, quotas and service-level requirements;
- configuration, feature flags and environment dependencies;
- business, safety, privacy and technical invariants;
- organizational-policy controls;
- ambiguities, aliases and unresolved conflicts;
- risks and threat-model findings;
- existing test assets and execution results;
- atomic coverage links;
- scenario universe and optimization decisions;
- approved/generated Test Models.

## Core semantic node contracts

The final schema may evolve, but it must be capable of representing at least the semantics below.

### Entity

Represents a business, technical or physical concept relevant to behavior.

Minimum semantic fields:

```yaml
id: entity.<stable-id>
name: <evidence-backed name>
kind: business | technical | physical | external | unknown
description: <optional normalized description>
fields: []
relationships: []
constraints: []
states: []
provenance: []
```

### Field / Attribute

```yaml
id: field.<stable-id>
entity_id: entity.<id>
name: <name>
data_type: <known type or unknown>
required: true | false | unknown
constraints: []
aliases: []
provenance: []
```

Do not infer type, nullability, uniqueness, length, formatting or aliases from naming conventions alone.

### Relationship

```yaml
id: relationship.<stable-id>
from_entity: entity.<id>
to_entity: entity.<id>
relationship_type: one_to_one | one_to_many | many_to_many | owns | references | contains | derived | unknown
cardinality: <optional structured value>
constraints: []
provenance: []
```

### Actor / Role / Group

Keep business actors, authentication roles and implementation groups separable. They may map to one another, but must not be assumed equivalent.

```yaml
actor:
  id: actor.<id>
  name: <name>
  provenance: []

role:
  id: role.<id>
  name: <name>
  provenance: []

mapping:
  actor_id: actor.<id>
  role_ids: []
  group_ids: []
  status: confirmed | proposed | conflicting | unresolved
  provenance: []
```

### Permission

```yaml
id: permission.<id>
subject_id: actor-or-role-id
resource: <entity/capability/interface>
action: <read/create/update/delete/execute/approve/etc>
scope: <resource/tenant/project/environment/etc>
effect: allow | deny | conditional
conditions: []
provenance: []
```

### State

```yaml
id: state.<id>
entity_id: entity.<id>
name: <evidence-backed state>
terminal: true | false | unknown
provenance: []
```

### Transition

A transition is richer than `from → to`. It must support the execution conditions needed for test design.

```yaml
id: transition.<id>
entity_id: entity.<id>
from_state: state.<id> | null
to_state: state.<id> | null
trigger:
  action_id: <optional>
  event_id: <optional>
actor_ids: []
role_ids: []
channel_ids: []
preconditions: []
guards: []
postconditions: []
side_effects: []
exceptions: []
classification: normal | exception | contingency | invalid | recovery | unknown
provenance: []
```

A transition must not be created merely because source code contains an assignment. The model must preserve whether the transition is contractual, implementation-observed, policy-derived or unresolved.

### Channel

A channel describes **how** behavior is initiated or observed, not what the business action necessarily means.

Examples of generic channel kinds include UI, API, CLI, event bus, queue, batch, device, import/export, physical operation or external integration.

```yaml
id: channel.<id>
name: <name>
kind: ui | api | cli | event | queue | batch | device | file | physical | external | other
interface_ids: []
provenance: []
```

### Action / Command / Event

```yaml
id: action.<id>
name: <name>
actor_ids: []
input_constraints: []
output_claims: []
side_effects: []
provenance: []
```

Events should distinguish producer, consumer, delivery semantics and ordering when known.

### Interface / API / Integration

```yaml
id: interface.<id>
kind: http_api | rpc | event | queue | file | database | device | ui | cli | other
producer: <component/system>
consumer: <component/system>
contract_source_ids: []
authentication: <known structure or unresolved>
authorization: <known structure or unresolved>
timeout: <value or unknown>
retry: <policy or unknown>
idempotency: <policy or unknown>
ordering: <guarantee or unknown>
failure_behavior: <claim/reference or unresolved>
implementation_symbols: []
provenance: []
```

Do not populate retry, timeout, idempotency, error codes or ordering unless supported by evidence.

### Verified interaction path

A manual execution path is evidence-bearing data, not decoration.

```yaml
id: path.<id>
kind: ui | api | cli | physical | mixed
steps:
  - locator_or_action: <verified instruction>
    evidence: []
verification_status: verified | partial | unresolved
```

Framework conventions or guessed menu names cannot make a path `verified`.

### Requirement and atomic criterion

```yaml
requirement:
  id: requirement.<id>
  title: <title>
  lifecycle: draft | approved | active | superseded | deprecated | unknown
  provenance: []

atom:
  id: atom.<id>
  requirement_id: requirement.<id>
  statement: <single testable behavioral/control proposition>
  dimensions:
    states: []
    actors: []
    channels: []
    boundaries: []
    timing: []
    failure_modes: []
  provenance: []
```

A requirement linked to one test is not automatically fully covered.

### Invariant

```yaml
id: invariant.<id>
statement: <property that should hold>
origin: CONTRACT | ORGANIZATIONAL_POLICY | RISK | IMPLEMENTATION
scope: <where it applies>
provenance: []
```

Risk-derived invariants require a defensible safety/security/data-integrity basis or approval before becoming normative.

### Ambiguity / Conflict / Alias

The Project Model must preserve uncertainty rather than resolving it invisibly.

```yaml
ambiguity:
  id: ambiguity.<id>
  question: <missing decision>
  affected_nodes: []
  evidence: []
  risk_of_guessing: <text>
  status: open | resolved

conflict:
  id: conflict.<id>
  claim_ids: []
  authority_decision: resolved | unresolved
  resolution_source: <optional>
```

Aliases must include evidence and confidence; similar labels are not automatically synonyms.

### Risk and Scenario

```yaml
risk:
  id: risk.<id>
  category: security | data | concurrency | resilience | time | performance | accessibility | observability | configuration | human_physical | other
  description: <failure mode>
  affected_nodes: []
  severity: <configured scale>
  provenance_or_derivation: []

scenario:
  id: scenario.<id>
  origin: CONTRACT | IMPLEMENTATION | ORGANIZATIONAL_POLICY | RISK | EXPLORATORY
  preconditions: []
  stimulus: <action/event>
  expected_invariant_or_oracle: <reference or unresolved>
  selected_for_test: true | false
  selection_reason: <risk/coverage/dedup explanation>
```

### Existing Test and Test Model

Existing tests are evidence assets and coverage candidates; they are not authoritative merely because they exist.

A generated Test Model should reference:

- objective;
- scenario IDs;
- atomic criterion IDs;
- origin;
- preconditions;
- test data properties;
- verified path references;
- manual actions;
- Expected Result oracle IDs;
- Pass/Fail/Blocked semantics;
- cleanup/isolation;
- risk links;
- readiness state;
- provenance.

## Universal provenance rule

Every semantic node that can influence a normative test must retain provenance. At minimum:

- source ID(s);
- exact location/span/symbol when available;
- extraction method/version;
- `inferred` flag;
- confidence;
- authority class;
- conflict state;
- snapshot/project identity.

Derived nodes retain links to the claims they were derived from. Provenance must be traversable in both directions where practical:

`test → oracle → claim → source`

and

`source → claims → requirements/risks → scenarios → tests`.

## Graph views

A graph database is optional. The logical graph is not.

Useful edges include:

- source → claim;
- claim → requirement/constraint/state/permission/etc.;
- requirement → atom;
- atom → oracle;
- atom → existing/generated test;
- entity → field/constraint/relationship/state;
- actor ↔ role/group;
- actor/role → permission;
- state → transition → channel/action/event;
- interface → implementation symbol;
- integration → producer/consumer;
- risk → scenario;
- scenario → selected test;
- test → oracle → evidence;
- conflict → affected claims/nodes.

## Matrices/views required for downstream test design

The model should support deriving, when applicable:

- actor/role/permission matrix;
- state-transition matrix;
- state × action × actor × channel matrix;
- entity/field/constraint matrix;
- interface/contract/implementation matrix;
- integration failure/retry/idempotency matrix;
- requirement-atom coverage matrix;
- risk-scenario-test matrix;
- environment/configuration matrix;
- verified-path map.

The engine should create only meaningful dimensions. Do not explode absent concepts into meaningless combinations.

## Verified paths

A UI/API/CLI/physical path must be observed in code, UI/design evidence, contract, manual/runbook or runtime evidence. A path guessed from framework conventions cannot make a case `READY`.

If the behavior is known but the path is not, the case remains unresolved/blocked for manual execution rather than receiving an invented path.

## Atomic coverage

Coverage operates on atomic behaviors/criteria, not merely requirement IDs. A requirement linked to one test can still contain uncovered:

- branches;
- exceptions;
- boundaries;
- roles/permissions;
- channels;
- states/transitions;
- failure/recovery modes;
- timing/performance clauses;
- security/privacy controls;
- concurrency conditions;
- configuration variants.

## Model integrity invariants

The implementation must eventually enforce at least:

1. every referenced node exists in the same allowed project/snapshot namespace;
2. normative test oracles resolve to valid provenance/authority;
3. inferred values cannot silently become contractual facts;
4. unresolved high-impact conflicts block dependent normative outputs;
5. verified paths require evidence;
6. deleted/superseded evidence invalidates or reclassifies dependent claims;
7. duplicates/aliases do not create fake coverage;
8. implementation observations remain distinguishable from approved contract;
9. scenario generation preserves the reason a scenario exists and why it was selected/rejected;
10. model serialization is versioned and reproducible.

## Implemented milestone boundary

M0 does **not** need to implement the full extraction engine. It must, however, create a Project Model skeleton and contracts that do not make the later semantics impossible or require a destructive redesign.

M0 should define stable IDs, project/snapshot scoping, provenance-bearing base types and enough schema shape for representative nodes such as entities, actors/roles, states/transitions, interfaces, requirement atoms, risks/scenarios and tests.

M1 implements bounded local inventory/parsing and conservative population from explicit
structured evidence plus raw OpenAPI declarations. Arbitrary natural-language semantic
interpretation is not implemented. M2 adds audit, atomic traceability, risk/scenario analysis
and coverage views; M3 adds manual test generation.

## Model versioning

The Project Model schema is versioned. Breaking schema changes require migration guidance. Every generated output records the schema version and project snapshot that produced it.
