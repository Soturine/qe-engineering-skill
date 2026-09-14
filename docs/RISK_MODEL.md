# Cross-Project Risk Model

Risk analysis supplements requirements; it does not rewrite them. Packs are activated by evidence/applicability rather than blindly generating every category.

## Risk classes

### Security
Authentication, authorization, horizontal/vertical privilege escalation, tenant/project isolation, injection, unsafe input, secret exposure, replay, abuse/rate, insecure defaults, logging/audit integrity and dependency/supply-chain risk.

### Privacy and compliance
Data minimization, purpose/scope, retention/deletion, consent/legal basis when applicable, sensitive-data exposure, export/erasure, auditability and jurisdiction/regulatory obligations. External standards become normative only when actually applicable/adopted.

### Data integrity
Lost updates, partial writes, duplicate processing, inconsistent aggregates, invalid relationships, stale cache, soft-delete behavior, import/export integrity and schema drift.

### Concurrency
Two users/actions racing for the same resource, double-submit, optimistic/pessimistic locking, asynchronous ordering and eventual consistency.

### Resilience and recovery
Timeout, retry, backoff, idempotency, offline/online recovery, service restart, queue duplication, delayed/out-of-order events, partial dependency outage, crash/restart and recovery after uncertain commit state.

### Time
Timezone, DST where relevant, boundary instants, expiration, scheduling, clock skew, date overlap, ordering timestamps and retention windows.

### Performance and capacity
Latency, throughput, payload size, dataset size, burst behavior, resource exhaustion and degradation. A performance TC needs a measurement protocol; a human stopwatch alone is rarely a defensible technical acceptance method.

### UX, accessibility and operability
Clear feedback, recoverability, keyboard/screen-reader concerns where applicable, no color-only meaning, operational pressure, destructive confirmation, error prevention and understandable status.

### Observability and auditability
Traceability of critical operations, stable event identity, actor/time/context, correlation, failure visibility and tamper resistance appropriate to scope.

### Configuration, deployment and compatibility
Feature flags, wrong environment, stale schema, migration failure, inactive integration, missing secret, incompatible versions, rolling deployment, configuration drift and backward/forward compatibility.

### Integration and contract drift
Breaking API/event/schema changes, unexpected nullability/types, incompatible consumers/producers, retry semantics, webhook duplication, queue ordering and dependency behavior changes.

### Safety and physical operation (when applicable)
Unsafe sequence, human error, device/sensor failure, stale physical state and software/physical divergence. Detailed scenarios belong in `HUMAN_PHYSICAL_FACTORS.md`.

### AI/agentic behavior (when applicable)
Prompt injection, tool misuse, context leakage, unsupported claims, non-deterministic drift, unsafe autonomous actions, model/provider changes, data poisoning and approval spoofing.

## Risk scoring

Use configurable ranking. A simple default may combine impact × likelihood × detectability, but do not imply numerical precision where evidence is weak. High/critical risk receives deeper coverage, stronger review and stronger evidence/measurement requirements.

## Risk-derived oracle rule

A credible risk justifies generating a scenario, not inventing the correct business outcome. If no defensible invariant/policy/contract exists, emit an exploratory charter or ambiguity for decision.
