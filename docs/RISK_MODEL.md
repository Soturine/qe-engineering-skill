# Cross-Project Risk Model

Risk analysis supplements requirements; it does not rewrite them.

## Risk classes

### Security

Authentication, authorization, horizontal/vertical privilege escalation, tenant isolation, injection, unsafe input, secret exposure, replay, abuse/rate, insecure defaults, logging/audit integrity, dependency/supply-chain risk.

### Data integrity

Lost updates, partial writes, duplicate processing, inconsistent aggregates, invalid relationships, stale cache, soft-delete behavior, export/import integrity.

### Concurrency

Two users/actions racing for the same resource, double-submit, optimistic/pessimistic locking, asynchronous order, eventual consistency.

### Resilience

Timeout, retry, backoff, idempotency, offline/online recovery, service restart, queue duplication, delayed/out-of-order events, partial dependency outage.

### Time

Timezone, DST where relevant, boundary instants, expiration, scheduling, clock skew, date overlap.

### Performance/capacity

Latency, throughput, payload size, dataset size, burst behavior, resource exhaustion. A performance TC needs a measurement protocol; a human stopwatch alone is rarely a defensible acceptance method.

### UX/accessibility/operability

Clear feedback, recoverability, keyboard/screen-reader concerns where applicable, no color-only meaning, operational pressure, destructive confirmation.

### Observability/auditability

Traceability of critical operations, stable event identity, actor/time/context, failure visibility, tamper resistance appropriate to scope.

### Configuration/deployment

Feature flags, wrong environment, stale schema, migration failure, inactive device/integration, missing secret, incompatible versions.

### AI/agentic behavior (when applicable)

Prompt injection, tool misuse, context leakage, unsupported claims, non-deterministic drift, unsafe autonomous actions, model/provider changes.

## Risk scoring

Use configurable risk ranking. A simple default may combine impact × likelihood × detectability, but do not imply numerical precision where evidence is weak. High-risk scenarios receive deeper coverage and stronger review/evidence requirements.
