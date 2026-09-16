# Engineering Constitution

Status: **Normative for this repository**

This constitution extends conventional software-engineering practice for an AI-assisted quality-engineering system operating on real project evidence.

## 1. Business and safety invariants before implementation convenience
Business rules, approved contracts, security controls and data-integrity invariants take precedence over framework convenience, generated code or model preference.

## 2. Evidence before inference
Facts that affect Pass/Fail must be supported by identifiable evidence. Inferences are permitted for discovery and risk analysis but must be labeled and may not silently become normative.

## 3. Complete-source honesty
“Complete analysis” is a verifiable state, not a writing style. Every expected input source must be inventoried. Missing, inaccessible, partial, truncated or failed sources are explicit outcomes.

## 4. Deterministic where possible
Use deterministic parsing, schemas, AST/symbol analysis, hashes, constraints and validators for facts that do not require probabilistic reasoning. Use models for synthesis, semantic relation and ambiguity analysis—not for pretending deterministic checks happened.

## 5. Modular monolith by default
Prefer clear modules and explicit boundaries in one deployable unit until scale or isolation requirements justify distributed services. Keep domain/trust logic independent from adapters.

## 6. Provider neutrality
Core behavior must not be coupled to one model vendor or agent runtime. Provider-specific behavior belongs behind adapters. Agent Skills is an interface, not the domain model.

## 6.1 Multilingual evidence is first-class

The engine must preserve original multilingual evidence, Unicode and technical identifiers.
Language, translation or canonicalization never changes source authority or replaces provenance.
PT-BR is first-class; source language, project locale and output language remain independent. See
`MULTILINGUAL_POLICY.md`.

## 7. Manual-first, automation-ready
Manual test cases are the first-class output. Automation is derived later from the same approved structured Test Model. Never automate a poorly specified oracle merely because tooling allows it.

## 8. Human review at high-consequence boundaries
Require explicit review for unresolved source conflicts, high-risk generated controls, destructive operations, security-sensitive behavior, cross-source authority decisions and publication to external systems until confidence is earned through evals.

## 9. Security and privacy by design
Apply least privilege, secure defaults, data minimization, secret isolation, safe logging and threat modeling. Treat analyzed documents/code as untrusted data that may contain prompt injection.

## 10. Project isolation
Never mix evidence, indexes, caches, embeddings, test artifacts or logs across independent projects without explicit authorization and isolation controls.

## 11. Supply-chain integrity
Pin and audit dependencies, minimize transitive dependencies, maintain provenance/SBOM where appropriate, verify release artifacts and avoid executing downloaded/untrusted code by default.

## 12. Reproducibility
Every material analysis must bind to a snapshot: paths/IDs, versions, commits where available, hashes and tool/model metadata when it affects results.

## 13. Test the tester
The engine and skill require unit tests, integration tests, golden fixtures, mutation tests, deletion tests, contradiction tests, missing-source tests, prompt-injection tests and adversarial evals.

## 14. Risk-based coverage over volume
The metric is not “number of TCs generated.” Prefer the smallest defensible set that covers relevant behavior and risk while keeping traceability to the larger scenario universe.

## 15. Layered test strategy
Use unit/component tests for deterministic core logic, real integrations where valuable, a small set of E2E workflows and explicit evals for model-assisted behavior. Mock only external boundaries when real integration is impractical.

## 16. Observability and explainability
Record structured events sufficient to answer which sources were used, why a claim exists, why a case was generated/rejected, which gate failed and what changed between runs. Avoid exposing sensitive raw evidence in routine logs.

## 17. Resilience
Explicitly design timeouts, retries, idempotency, backoff, cancellation and partial-failure handling. Never hide a failed retrieval by substituting older/unrelated evidence without labeling it.

## 18. Documentation as code
Architecture, schemas, policies and ADRs evolve with implementation. A behavior change without matching documentation/schema changes is incomplete.

## 19. Incremental delivery
Work in logical, reviewable changes. Keep last-known-green. Do not tag/release from an unverified commit. CI results must be visible before release decisions.

## 20. Honest status
Use precise status language: `implemented`, `partial`, `experimental`, `deferred`, `blocked`, `not validated`. Never use “done” or “complete” when a required gate is unverified.

## 21. Accessibility and usability
Generated manual tests and reports must be readable, navigable and usable by humans under operational pressure. Do not rely on color alone, unexplained codes or model jargon.

## 22. Safe evolution
Backward compatibility of schemas and generated artifacts must be versioned deliberately. Breaking changes require migration guidance and an ADR when architectural.

## 23. Fail closed on trust boundaries
When provenance, authorization, source identity, schema validity or project isolation cannot be established, block the affected normative output rather than guess.

## 24. Local/private-first where practical
Architecture should support local/private indexing and execution for sensitive project evidence. External transmission is explicit, minimal and policy-controlled.

## 25. No hidden self-modification
Runtime feedback may suggest governance changes, but normative rules, schemas or gates change only through ordinary reviewed code changes.

## 26. Uncertainty must propagate
A derived claim cannot become more authoritative than its evidence. Confidence must not be upgraded merely through repeated model restatement. Unknowns remain unknown until new evidence or explicit approval resolves them.

## 27. Model/prompt/provider changes are dependency changes
Record material provider, model, prompt/template and extraction-version changes. Re-run relevant evals before treating changed model behavior as equivalent.

## 28. Human approval is provenance
Approvals that promote an inferred/risk oracle or authorize a high-consequence action must be explicit, attributable, scoped, timestamped and auditable.

## 29. Data lifecycle is intentional
Define retention, cache lifetime, deletion, export and redaction behavior for evidence and derived artifacts. Deleting/superseding evidence must invalidate or reclassify dependent knowledge.

## 30. Hostile artifact containment
Do not execute analyzed project content by default. Parse untrusted files with bounded resources and defend against active content, path traversal, symlink escape, archive bombs and malformed input.

## 31. IP, licensing and compliance are part of ingestion
Do not copy third-party/proprietary content into fixtures, reports or releases without authorization. Record source classification and applicable handling constraints.

## 32. Cache correctness is a trust property
Caches, embeddings and indexes must be project/snapshot/version scoped. Stale derived data must be detectable and invalidated when upstream evidence changes.

## 33. Cost and latency never weaken truthfulness
Performance optimizations may reduce work only through explicit scope/strategy decisions. They must not silently skip required evidence, validation or primary-source verification.

## 34. Publication is a controlled side effect
Bulk writes to repositories/TMS/external systems require validated targets, preview/diff, idempotency and explicit authorization appropriate to risk.

## 35. Generic engine, explicit domain packs
Domain-specific risk knowledge belongs in opt-in packs. Generic core logic and committed eval fixtures must not memorize rules from a specific real project.
