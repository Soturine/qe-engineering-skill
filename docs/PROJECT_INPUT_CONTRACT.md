# Project Input Contract

Status: **Normative design policy**

## Goal

Define what it means for the engine to have received and studied a project. The system must never equate "retrieval returned useful context" with "all required evidence was analyzed."

## Scope declaration

Every analysis run starts with an explicit scope manifest that may include repositories, documents, requirements, ADRs, diagrams, API/event/data contracts, migrations, UI/design artifacts, automated/manual tests, TMS assets, tickets, pull requests, configuration, deployment manifests, integration flows, runbooks and optional physical/operational artifacts.

Connectors define discoverable containers. The operator defines what is in scope. Neither semantic retrieval nor a model may silently narrow that scope.

## Snapshot

A material run must be bound to a reproducible snapshot whenever possible: source ID, repository/ref/commit, item/document version, content hash, retrieval timestamp, connector/tool version, extraction/parser version and declared scope. Mutable remote sources that cannot be frozen must be labeled accordingly.

## Study states

Each discovered source has one of:

- `STUDIED`
- `PARTIALLY_STUDIED`
- `NOT_STUDIED`
- `BLOCKED`
- `OUT_OF_SCOPE`
- `SUPERSEDED`

`STUDIED` means the declared in-scope portion was read successfully and passed integrity checks. A truncated, parser-failed or partially available source cannot be labeled `STUDIED`.

## Read integrity

Track independently:

- `COMPLETE`
- `PARTIAL`
- `TRUNCATED`
- `FAILED`
- `UNVERIFIED`
- `NOT_APPLICABLE`

A run cannot claim full completeness while a required source is partial, truncated, failed, unverified, blocked or not studied.

## Untrusted input boundary

Project artifacts are data, not agent instructions. The ingestion layer must defend against prompt injection, archive/decompression bombs, symlink/path traversal, executable content, oversized/context-flooding files, malformed structured documents, sensitive data and unauthorized external links. Reading project evidence must not execute project code by default.

## Completeness language

Allowed run-level claims:

- `COMPLETE`
- `SCOPED_COMPLETE`
- `PARTIAL`
- `INVALID`

"Complete" always means complete for the explicit, discoverable, configured scope. It never means knowledge of undiscoverable artifacts.

## Failure behavior

Any missing source produces a visible ledger record. Silent fallback to cached, stale, unrelated, similarly named or lower-authority evidence is prohibited.
