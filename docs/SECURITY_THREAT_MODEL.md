# Security Threat Model

Status: **Baseline threat model**

## Assets

Protect proprietary source/documents, requirements/business rules, credentials/tokens, personal/sensitive data, project-isolation boundaries, provenance/approval records, generated artifacts, external write capability and indexes/caches/embeddings.

## Trust boundaries

Major boundaries:

- operator → engine;
- connector → ingestion;
- project evidence → parsers/models;
- model provider → engine;
- cache/vector store → analysis;
- engine → external TMS/repository;
- one project/snapshot → another.

## Threats and required controls

### Prompt injection / instruction confusion
Project files are untrusted data. Embedded instructions cannot modify system/skill policy or authorize tools.

### Cross-project leakage
Namespace every cache/index/run. Enforce project/snapshot identity on reads and writes. Add adversarial same-name fixtures.

### Secret/data exfiltration
Minimize extraction, redact reports, avoid logging raw sensitive content, and require explicit policy before sending sensitive evidence to external providers.

### Malicious files
Defend against path traversal, symlink escape, archive bombs, oversized payloads, malformed parsers, active content and accidental code execution. Prefer sandboxed/document-only parsing.

### SSRF / connector abuse
Restrict network targets/connectors to authorized scopes. Do not follow arbitrary artifact-provided links automatically.

### Tool misuse
Use least privilege. Destructive/bulk writes need explicit approval, preview and idempotency.

### Cache/index poisoning
Bind derived data to hashes, project/snapshot and versioned extractors/models. Invalidate on mutation/deletion.

### Approval spoofing
Human approval is a first-class auditable record, not a free-form model assertion.

### Supply chain
Pin/audit dependencies, generate SBOM where appropriate, verify release artifacts and minimize executable third-party code.

### Output injection
Escape/validate exports. Consider spreadsheet formula injection, markup/script injection and unsafe generated commands.

### Denial of service / context flooding
Bound file size, nesting, archive expansion, token budgets and concurrency while surfacing what was skipped; limits must not silently create `COMPLETE` results.

## Security testing

Security controls are tested in unit/integration/eval suites. Critical trust-boundary failures are release blockers.
