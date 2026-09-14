# ADR 0001: versioned trust contracts

Status: accepted for M0.

Use strict Pydantic data contracts and check in their reproducible Draft 2020-12
JSON Schemas. JSON Schema independently validates serialized shapes; deterministic
cross-artifact validators enforce policy. Both share version 1.0. CI rejects drift.
This avoids separately maintained, contradictory representations. Schemas and
domain contracts are established before policy validators and generation.

Every live reference includes project and snapshot identity. Historical identity
is a distinct opaque metadata type: importing history grants no destination authority.
Semantic nodes are a discriminated union with typed relationships, not arbitrary
property bags. Unknown interface guarantees remain null.

Approval binds a proposal digest, operation IDs, actor, authority and both snapshots.
An operation binds the artifact digest, payload digest and target version. Validation
will require a separately supplied trusted approval context; artifact input cannot
self-authorize. M0 has no external write executor. Destructive operations are absent
from the normal operation enum. Content digests are integrity bindings, not signatures.

M0 consumes declared evidence metadata. Verifying original files, extracting semantics,
authenticating reviewers and executing publication belong to later adapters. Structural
validation cannot prove that arbitrary natural-language claims faithfully quote a source.
The CLI must report this boundary rather than claim semantic correctness or publication.

Breaking contract changes require a new version and migration guidance. There is no
pre-existing executable schema to migrate in 1.0. No production generator or M1/M2
extraction is introduced.
