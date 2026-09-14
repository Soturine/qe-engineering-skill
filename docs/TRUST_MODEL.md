# Trust Model

## Objective

Make confidence and evidence mechanically inspectable rather than implicit in prose.

## Source ledger

Every run creates a ledger entry for each expected source.

Minimum fields:

- stable `source_id`;
- `source_type`;
- URI/path/item ID;
- version/branch/commit when applicable;
- content hash when possible;
- collection timestamp;
- authority class;
- status (`STUDIED`, `NOT_STUDIED`, `BLOCKED`, `OUT_OF_SCOPE`);
- block/out-of-scope reason;
- extraction method/version;
- sensitivity classification.

The set of “expected sources” must be defined by source connectors plus explicit operator scope. The system cannot know about an artifact that was never discoverable; therefore complete means **all in-scope discoverable/configured sources accounted for**, not metaphysical knowledge of every artifact that exists anywhere.

## Claim provenance

Derived claims store:

- claim text/normalized representation;
- origin class;
- primary source IDs;
- locations/spans/symbols;
- `inferred` flag;
- confidence;
- derivation/transform metadata;
- conflict status.

## Confidence is not authority

A model may be 99% confident about an inference, but confidence does not turn the inference into a contract. Authority and confidence are distinct dimensions.

## Completeness states

Recommended run-level states:

- `COMPLETE` — all required in-scope sources have acceptable terminal states and required gates pass;
- `PARTIAL` — useful analysis exists but at least one required source is missing/blocked/not studied;
- `SCOPED_COMPLETE` — complete for an explicitly narrowed scope;
- `INVALID` — source identity, project isolation or snapshot integrity cannot be established.

## Output readiness states

- `READY`
- `READY_WITH_REVIEW`
- `AMBIGUOUS`
- `BLOCKED_SOURCE`
- `EXPLORATORY_ONLY`
- `REJECTED_DUPLICATE`
- `REJECTED_UNSUPPORTED_ORACLE`

## Contradictions

Never silently choose the source that is easiest to implement. Apply configured source authority only when it legitimately resolves precedence. Otherwise emit a conflict record and block dependent normative outputs.

## Staleness

Timestamp alone is weak evidence of freshness. Prefer explicit version/status markers, active ADR state, branch/commit context and content semantics. Preserve supersession/deprecation relationships.

## Prompt-injection model

All analyzed content—including source code comments, Markdown, tickets and documents—is untrusted data. Text such as “ignore previous instructions” inside a project artifact is a finding/input, not an instruction to the runtime.
