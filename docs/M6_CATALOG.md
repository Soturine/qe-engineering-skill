# M6 Planning Catalog

Status: **DEFERRED_TO_M6**

This catalog records future change-impact, orchestration, benchmark, retrieval and release-hardening work. It does not authorize implementation during M3 and does not change the M0–M2 trust model.

## M6-A — Change impact

Status: **DEFERRED_TO_M6**

Catalog the dependency chain `source/file → Claim → Requirement/Atom → Scenario → Test Model → Automation → Execution Evidence`, including stale/invalid/review propagation, PR/diff analysis, regression selection, incremental indexing and a dependency graph.

```text
source
└── claim
    └── requirement/atom
        └── scenario
            └── test case
                └── automation
                    └── execution evidence
```

## M6-B — QA pipeline / CI-style orchestration

Status: **DEFERRED_TO_M6**

Expose provider- and TMS-neutral artifacts, commands and gates for existing CI systems rather than replacing GitHub Actions, Azure Pipelines or Jenkins.

```text
Source Inventory
→ Ingestion
→ Trust Gate
→ Audit
→ Coverage/Risk Gate
→ Test Authoring
→ Generation Gate
→ Automation Validation
→ Execution Evidence
→ Quality Report
```

Potential artifact states are `VALID`, `STALE`, `INVALID`, `BLOCKED`, `REVIEW_REQUIRED` and `SUPERSEDED`.

## M6-C — Downstream artifact invalidation

Status: **DEFERRED_TO_M6**

Represent dependencies as `Artifact B depends_on Artifact A @ hash X`. When A changes, mark B `STALE` with reason `UPSTREAM_CHANGED`; do not destructively rewrite it. The intended propagation is Project Model → M2 → M3 Test Model → M5 automation.

M3 may implement only direct Project Model and M2 input-hash binding needed to reject stale generation inputs.

## M6-D — Automated competitor/self benchmark

Status: **DEFERRED_TO_M6**

Run the same synthetic fixture, model, reasoning budget, tool permissions and context budget through isolated implementations, then normalize and score JSON/Markdown/HTML reports. Competitor manifests must pin repository, exact commit or tag, skill path, license/metadata and runner configuration; a moving `main` is not a valid benchmark dependency.

## M6-E — External skill sandboxing

Status: **DEFERRED_TO_M6**

Run downloaded skills only in a disposable sandbox/container with no host secrets or cloud credentials, a bounded filesystem, network disabled unless explicitly required, CPU/time/memory limits, an isolated workdir, immutable fixtures, captured output/artifacts and repository/commit provenance. Arbitrary downloaded code must not run directly on the trusted host by default.

## M6-F — Benchmark metrics

Status: **DEFERRED_TO_M6**

- Correctness: atomic behavior recall, traceability accuracy, unsupported-oracle rate, hallucinated-path rate, false-requirement rate and conflict detection.
- Audit: gap precision/recall, duplicate and stale-asset detection, non-executable detection and oracle-support classification.
- Manual quality: executability, step completeness, Expected Result provenance, Pass/Fail/Blocked correctness, cleanup/isolation, parameterization, Shared Step usefulness and redundancy.
- Safety: prompt-injection resistance, cross-project leakage, risk-to-requirement leakage, destructive-proposal rate and unsupported-evidence handling.
- Efficiency: total cases, coverage per case, redundancy, runtime and measurable token/context use.

## M6-G — Self-regression benchmark

Status: **DEFERRED_TO_M6**

Compare release candidates with a pinned known-green baseline. Candidate hard gates include unsupported normative-oracle rate greater than zero, hallucinated verified-path rate greater than zero, or cross-project leakage greater than zero. Other thresholds require measured evidence.

## M6-H — Fair cross-model matrix

Status: **DEFERRED_TO_M6**

Catalog and evaluate `skill × model × reasoning effort`, holding fixtures, context, tools, permissions and timeouts equivalent where practical. Measure both overall quality and whether the skill improves smaller models.

## M6-I — Independent Astra6 audit

Status: **DEFERRED_TO_M6**

Near M6 completion, use Astra6 Light/Medium if available for an independent architecture, security and quality review covering documentation/code divergence, overengineering, missing edges, untested contracts, trust bypass, security weakness, schema drift, false completeness and benchmark bias. Reviewer output is evidence, not authority. Each accepted finding must follow `finding → reproduce → failing test/eval → fix → revalidate`.

## M6-J — Release hardening

Status: **DEFERRED_TO_M6**

Catalog architecture, schema/version, security/threat-model, fuzz/adversarial, performance/resource-bound, cross-platform, supply-chain, SBOM/provenance, documentation consistency, packaging, benchmark baseline and release-evidence reviews. Version/tag only after green CI.

## M6-K — Advanced retrieval when proven

Status: **DEFERRED_TO_M6**

Catalog vector retrieval, GraphRAG and richer dependency graphs. Adopt them only when evaluations show a measurable benefit without weakening provenance. Retrieval-derived normative claims must still resolve to primary evidence.
