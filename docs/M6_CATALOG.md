# M6 Planning Catalog

Status: **DEFERRED_TO_M6**

This catalog records future change-impact, orchestration, benchmark, retrieval and release-hardening
work. It does not authorize implementation during M4 and does not change the validated M0–M3 trust,
audit, or generation contracts.

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

## M6-L — Retrospective whole-system audit

Status: **DEFERRED_TO_M6**

M6 requalifies the complete M0→M5 system, not only M6 code. Tier 1 covers M3 generation,
M0 trust, M5 oracle-preserving automation and cross-layer behavior. Tier 2 covers M2 analysis,
M1 ingestion and M4 integration/approval/sync behavior. M3 receives the heaviest review because
it first converts analysis into operational Test Cases.

## M6-M — Independent audit must try to break M3

Status: **DEFERRED_TO_M6**

Attempt path invention, implementation-to-contract leakage, risk-to-oracle leakage, silent
conflict resolution, clone assumption leakage, history mutation, Shared Step result propagation
and stale-M2 acceptance. Compare documentation, schemas, code, tests, evals, CLI and real generated
outputs rather than trusting milestone evidence alone.

## M6-N — Revalidate M0 across later architecture

Status: **DEFERRED_TO_M6**

For every M0 invariant, verify preservation through M1, M2, M3, M4 and M5. In particular, audit
whether programmatic oracle creation, external publication or automation introduces a bypass that
was absent when M0 was tested in isolation.

## M6-O — Findings become engineering evidence

Status: **DEFERRED_TO_M6**

Record each candidate finding with ID, claim, severity, evidence, reproduction, expected invariant
and actual result. A reviewer is not authority. Use `finding → reproduce → failing test/eval → fix
→ targeted validation → full suite → benchmark regression`; close unconfirmed findings with
evidence and avoid speculative refactors.

## M6-P — Two-pass independent audit

Status: **DEFERRED_TO_M6**

When Astra6 Light/Medium are available, use Light for a broad architecture/docs/complexity/trust
scan, then Medium only for credible findings and Tier 1 areas: M0, M3, M5, cross-layer behavior,
benchmark integrity and security.

## M6-Q — Pre/post hardening benchmark

Status: **DEFERRED_TO_M6**

Run the pinned automated benchmark before and after accepted M6 fixes. Report executability,
false-oracle/fake-path rates, gap recall, clone errors and redundancy so hardening is measurable.

## M6-R — Quality/trust and efficiency together

Status: **DEFERRED_TO_M6**

Principle: **Optimize around the trust boundary, never through it.** Track runtime, tokens,
context, case count, redundancy, coverage per case, output size and measurable cost alongside
atomic coverage recall, unsupported-oracle and hallucinated-path rates, false requirements,
traceability, executability, conflict detection, injection resistance and project isolation.

Priority is minimum quality → trust gates → security → provenance → correctness → optimization.

## M6-S — Hard gates are not trade-offs

Status: **DEFERRED_TO_M6**

Unsupported normative oracles, hallucinated verified paths and cross-project leakage above zero
are unacceptable regressions. Runtime/token savings never compensate for a trust-gate failure.

## M6-T — Efficiency frontier

Status: **DEFERRED_TO_M6**

Use a Pareto-style view rather than one weighted vanity score. A result dominates only when it
preserves required quality and perfect hard-gate trust while improving measured efficiency; a
cheaper result with degraded quality or trust cannot win.

## M6-U — Progressive depth

Status: **DEFERRED_TO_M6**

Evaluate Light, Medium and Deep analysis depths. Light supports deterministic CI checks, Medium
standard analysis and Deep release/ambiguity hardening. Depth may omit optional analysis but may
never weaken provenance, oracle, isolation or security gates.

## M6-V — Semantic reasoning mode benchmark

Status: **DEFERRED_TO_M6**

Compare deterministic-only, deterministic-plus-heuristics and deterministic-plus-semantic-provider
modes using identical pinned fixtures and evaluation contracts. Measure requirement/constraint
recall, false requirements, missed constraints, actor/state/relationship errors, conflict
detection, provenance/span accuracy, unsupported oracles, hallucinated paths, runtime, tokens,
context and cost. More extracted records do not imply better quality. Provider caches must bind to
source hash, provider/model/version, prompt/template/config and project/snapshot.
