# ADR 0002: provider-neutral semantic reasoning boundary

Status: accepted for M4.H1.

M4 introduces a synchronous typed `ReasoningProvider` protocol with four bounded operations:
extract, relate, synthesize, and probe scenarios. Provider-specific SDKs and credentials remain in
optional adapters; the core owns request bounds, project/snapshot scope, source excerpts and hashes,
provider/model/version identity, operation dispatch, result binding, and fail-closed status.

Provider responses contain untrusted proposals, not Project Model facts. Later M4 candidate gates
must preserve their provenance and uncertainty before any downstream use. The boundary cannot
change source authority, produce an external write, or bypass M0–M3 validation. Deterministic-only
operation uses no provider and produces an explicit `NOT_REQUESTED` result.

The initial protocol is synchronous to match the local modular-monolith CLI. Timeouts are part of
the request contract; adapters must enforce them, and the core also rejects responses returned
after the configured interval. Provider exceptions and timeouts become structured results without
copying possibly sensitive exception messages. Resource and provenance-bound violations are
rejected rather than truncated silently.

No live provider adapter or network dependency is included in M4.H1. A deterministic static
provider supports unit/component tests and offline integration. Async/provider-specific adapters
may be added later without changing candidate authority semantics.
