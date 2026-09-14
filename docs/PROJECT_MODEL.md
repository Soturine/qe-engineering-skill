# Normalized Project Model

Status: **Target intermediate representation**

## Purpose

The Project Model separates project understanding from test generation. Agents must first build and validate a normalized evidence-backed model; they must not generate test cases directly from arbitrary retrieved chunks.

## Core sections

A project model should represent, when applicable:

- run/snapshot identity;
- Source Ledger;
- extracted claims and source spans/symbols;
- requirement atoms and acceptance criteria;
- entities, fields, relationships and constraints;
- actors, roles, groups and permissions;
- states, transitions, guards, exceptions and channels;
- UI locations and interaction paths **only when verified**;
- APIs, events, queues, files and integration contracts;
- database/migration constraints;
- timings, limits, quotas and service-level requirements;
- configuration/feature flags/environment dependencies;
- business/technical invariants;
- organizational-policy controls;
- ambiguities, aliases and unresolved conflicts;
- risks and threat-model findings;
- existing test assets/results;
- atomic coverage links;
- scenario universe and optimization decisions;
- approved/generated Test Models.

## Universal provenance rule

Every semantic node that can influence a normative test must retain provenance. At minimum:

- source ID(s);
- location/span/symbol;
- extraction method;
- inferred flag;
- confidence;
- conflict state.

Derived nodes retain links to the claims they were derived from.

## Graph views

The implementation may expose graph views without requiring a graph database. Useful edges include:

- requirement → atom;
- atom → oracle;
- atom → existing test;
- entity → field/constraint;
- actor → permission;
- state → transition → channel;
- interface → implementation symbol;
- risk → scenario;
- scenario → selected test;
- test → oracle → evidence.

## Verified paths

A manual UI/API path is a claim, not decoration. It must be observed in code/UI/manual/runtime evidence or parameterized/left unresolved. A path guessed from framework conventions cannot make a case `READY`.

## Atomic coverage

Coverage operates on atomic behaviors/criteria, not merely requirement IDs. A requirement linked to one test can still contain uncovered branches, exceptions, boundaries, roles, channels, states, failure modes, timing clauses or security controls.

## Model versioning

The Project Model schema is versioned. Breaking schema changes require migration guidance. A generated output records which schema version produced it.
