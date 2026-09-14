# Trust Model

## Objective

Make evidence, authority, uncertainty and completeness mechanically inspectable rather than implicit in prose.

## Source Ledger

Every run creates a ledger entry for each discovered/expected source.

Minimum fields:

- stable `source_id`;
- `source_type`;
- locator (URI/path/item ID);
- version/branch/commit when applicable;
- content hash when possible;
- collection timestamp;
- authority class and lifecycle state;
- study status;
- read integrity;
- required/in-scope flags;
- block/out-of-scope reason;
- extraction method/version;
- sensitivity/handling classification.

Study statuses:

- `STUDIED`
- `PARTIALLY_STUDIED`
- `NOT_STUDIED`
- `BLOCKED`
- `OUT_OF_SCOPE`
- `SUPERSEDED`

Read integrity:

- `COMPLETE`
- `PARTIAL`
- `TRUNCATED`
- `FAILED`
- `UNVERIFIED`
- `NOT_APPLICABLE`

Complete means **all required in-scope discoverable/configured sources accounted for under the declared snapshot/scope**, not knowledge of undiscoverable artifacts.

## Claim provenance

Derived claims store:

- normalized claim;
- origin class;
- primary source IDs;
- exact locations/spans/symbols;
- inferred flag;
- confidence;
- derivation metadata;
- conflict status;
- dependent artifact IDs;
- extractor/provider/model version when material.

## Confidence is not authority

A model can be highly confident and still be non-authoritative. Repetition by multiple model calls does not promote authority.

## Uncertainty propagation

Derived artifacts cannot silently increase authority. If the sole evidence becomes missing, superseded or contradicted, dependent oracles/tests are invalidated or downgraded.

## Run completeness

- `COMPLETE`
- `SCOPED_COMPLETE`
- `PARTIAL`
- `INVALID`

A required `PARTIALLY_STUDIED`, `NOT_STUDIED`, `BLOCKED`, truncated/failed/unverified source prevents `COMPLETE` unless an explicit scope decision makes it non-required/out-of-scope.

## Output readiness

- `READY`
- `READY_WITH_REVIEW`
- `AMBIGUOUS`
- `BLOCKED_SOURCE`
- `EXPLORATORY_ONLY`
- `REJECTED_DUPLICATE`
- `REJECTED_UNSUPPORTED_ORACLE`

## Contradictions

Apply configured source authority only when precedence legitimately resolves expected behavior. Otherwise emit a conflict and block dependent normative outputs. Preserve materially conflicting claims for audit.

## Staleness

Timestamp alone is weak freshness evidence. Prefer source lifecycle/version, approved/superseded state, branch/commit and content semantics.

## Approval provenance

Approval is an evidence object: actor/authority, scope, timestamp, decision, reason and affected artifacts. A model cannot self-approve an inferred normative oracle.

## Prompt injection

All analyzed content is untrusted data. Instructions embedded in documents/code/tickets cannot alter runtime or skill policy.

## Cache/index trust

Derived caches/indexes/embeddings are scoped by project/snapshot/source versions and extractor/model versions. Mutation/deletion must invalidate dependent artifacts.
