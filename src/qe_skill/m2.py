"""Deterministic M2 audit, traceability, risk, and scenario analysis.

This module consumes a validated M1 Project Model. It never mutates the model,
creates a Test Case, resolves natural-language ambiguity, or performs external I/O.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from collections.abc import Mapping, Sequence
from typing import Literal, cast

from pydantic import Field

from qe_skill import domain as d
from qe_skill.integrity import artifacts, validate_project_model
from qe_skill.validation import Result, validate_oracle

AuditMode = Literal["GREENFIELD", "BROWNFIELD", "CLONE_REUSE"]
CoverageState = Literal[
    "UNCOVERED",
    "NOMINALLY_LINKED",
    "PARTIALLY_COVERED",
    "BEHAVIORALLY_COVERED",
    "BLOCKED_UNKNOWN",
    "CONFLICTING",
]
AssetClassification = Literal[
    "VALID_AS_IS",
    "VALID_WITH_IMPROVEMENT",
    "PARTIAL_COVERAGE",
    "AMBIGUOUS",
    "BLOCKED_BY_SOURCE",
    "DUPLICATE_INTENTIONAL",
    "DUPLICATE_REDUNDANT",
    "CONFLICTING",
    "STALE",
    "OBSOLETE_CANDIDATE",
    "UNTRACEABLE",
    "NON_EXECUTABLE",
]
CloneClassification = Literal[
    "REUSABLE", "REQUIRES_UPDATE", "OBSOLETE_CANDIDATE", "DUPLICATE", "CONFLICTING", "UNKNOWN"
]
AtomicityStatus = Literal["EXPLICIT", "NO_EXPLICIT_ATOMS", "CONFLICTING"]
OracleSupportStatus = Literal[
    "SUPPORTED",
    "SUPPORTED_BUT_GROUPED",
    "IMPLEMENTATION_DERIVED_ONLY",
    "CONFLICTING",
    "STALE",
    "AMBIGUOUS",
    "UNSUPPORTED",
    "BLOCKED_BY_SOURCE",
]
ProposalKind = Literal[
    "ADD_COVERAGE",
    "IMPROVE_PRECONDITIONS",
    "CLARIFY_EXPECTED_RESULT",
    "SPLIT_GROUPED_ORACLE",
    "PARAMETERIZE_DATA",
    "ADD_CLEANUP",
    "ADD_TRACEABILITY",
    "MARK_AMBIGUITY",
    "REVIEW_STALE_OR_OBSOLETE",
    "CREATE_REVISION_OR_REPLACEMENT",
    "ADD_RISK_SCENARIO",
    "SHARED_STEP_CANDIDATE",
]


class AnalysisConfig(d.Record):
    max_scenarios: int = Field(default=100, ge=1, le=10_000)
    max_pairwise_combinations: int = Field(default=24, ge=1, le=1_000)
    risk_scale: tuple[str, ...] = ("low", "medium", "high", "critical")


class AtomicityResult(d.Artifact):
    requirement: d.Ref
    atoms: list[d.Ref]
    status: AtomicityStatus
    rationale: str = Field(min_length=1)
    evidence: list[d.Ref]
    review_required: bool


class TraceabilityEdge(d.Artifact):
    source: d.Ref
    target: d.Ref
    relation: Literal[
        "REQUIREMENT_HAS_ATOM",
        "REQUIREMENT_NOMINALLY_LINKED_TO_TEST",
        "ATOM_COVERED_BY_TEST",
        "STATE_COVERED_BY_TEST",
        "ACTOR_COVERED_BY_TEST",
        "CHANNEL_COVERED_BY_TEST",
        "RISK_COVERED_BY_TEST",
        "TEST_USES_ORACLE",
        "RISK_PROPOSES_SCENARIO",
    ]
    evidence: list[d.Ref]


class AtomCoverage(d.Artifact):
    requirement: d.Ref
    atom: d.Ref
    tests: list[d.Ref]
    state: CoverageState
    rationale: str = Field(min_length=1)


class CoverageReport(d.Artifact):
    atoms: list[AtomCoverage]
    nominal_linked_requirements: int = Field(ge=0)
    total_requirements: int = Field(ge=0)
    behaviorally_covered_atoms: int = Field(ge=0)
    total_explicit_atoms: int = Field(ge=0)
    denominator_reliable: bool
    limitation: str | None = None


class AuditFinding(d.Artifact):
    asset: d.Ref | None
    classification: AssetClassification | None = None
    kind: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    supporting_evidence: list[d.Ref]
    impacted: list[d.Ref]
    severity: Literal["INFO", "LOW", "MEDIUM", "HIGH", "CRITICAL"]
    confidence: Literal["DETERMINISTIC", "REVIEW_REQUIRED"]
    proposed_action: str = Field(min_length=1)
    human_clarification_required: bool


class OracleSupportFinding(d.Artifact):
    test: d.Ref
    oracle: d.Ref | None
    expected_result_index: int = Field(ge=0)
    status: OracleSupportStatus
    rationale: str = Field(min_length=1)
    evidence: list[d.Ref]


class RiskAnalysisRecord(d.Artifact):
    source_risk: d.Ref
    category: str = Field(min_length=1)
    origin: Literal["RISK"] = "RISK"
    affected: list[d.Ref]
    evidence: list[d.Ref]
    rationale: str = Field(min_length=1)
    impact: str = Field(min_length=1)
    likelihood: str = "unknown"
    detectability: str = "unknown"
    rank: int | None = Field(default=None, ge=0)
    review_required: bool


class ScenarioRecord(d.Artifact):
    origin: d.Origin
    technique: Literal[
        "CRITERION",
        "EQUIVALENCE_PARTITION",
        "BOUNDARY_VALUE",
        "DECISION_TABLE",
        "STATE_TRANSITION",
        "PAIRWISE",
        "RISK_PACK",
    ]
    source_requirement: d.Ref | None = None
    source_atom: d.Ref | None = None
    source_risk: d.Ref | None = None
    actor: d.Ref | None = None
    pre_state: d.Ref | None = None
    stimulus: d.Ref | None = None
    data_partition: str | None = None
    channel: d.Ref | None = None
    constraint_values: list[str] = Field(default_factory=list)
    oracle: d.Ref | None = None
    rationale: str = Field(min_length=1)
    readiness: Literal["READY_FOR_M3", "REVIEW_REQUIRED", "EXPLORATORY", "BLOCKED"]


class ScenarioDisposition(d.Artifact):
    scenario: d.Ref
    disposition: Literal[
        "SELECTED",
        "MERGED",
        "PARAMETERIZED_CANDIDATE",
        "COVERED_BY_ANOTHER_LAYER",
        "DEFERRED",
        "EXPLORATORY",
        "BLOCKED",
        "REJECTED_UNSUPPORTED_OR_REDUNDANT",
    ]
    rationale: str = Field(min_length=1)


class ImprovementProposal(d.Artifact):
    asset: d.Ref | None
    kind: ProposalKind
    rationale: str = Field(min_length=1)
    related: list[d.Ref]
    proposal_only: Literal[True] = True
    external_operations: Literal[False] = False


class TraceabilityGraph(d.Artifact):
    edges: list[TraceabilityEdge]


class AuditFindings(d.Artifact):
    findings: list[AuditFinding]
    oracle_findings: list[OracleSupportFinding]
    history_summary: dict[str, dict[str, int]]


class RiskAnalysis(d.Artifact):
    risks: list[RiskAnalysisRecord]


class ScenarioUniverse(d.Artifact):
    scenarios: list[ScenarioRecord]
    dispositions: list[ScenarioDisposition]


class ProposalSet(d.Artifact):
    proposals: list[ImprovementProposal]
    proposal_only: Literal[True] = True
    external_operations: Literal[False] = False


class M2AnalysisReport(d.Artifact):
    mode: AuditMode
    status: Literal["COMPLETE", "PARTIAL", "INVALID"]
    source_completeness: d.Completeness
    atomicity: list[AtomicityResult]
    traceability: list[TraceabilityEdge]
    coverage: CoverageReport
    findings: list[AuditFinding]
    oracle_findings: list[OracleSupportFinding]
    history_summary: dict[str, dict[str, int]]
    clone_classifications: dict[str, CloneClassification]
    risks: list[RiskAnalysisRecord]
    scenarios: list[ScenarioRecord]
    dispositions: list[ScenarioDisposition]
    proposals: list[ImprovementProposal]
    limitations: list[str]
    input_model_hash: d.Digest
    deterministic: Literal[True] = True
    network_used: Literal[False] = False
    external_writes: Literal[False] = False
    historical_assets_mutated: Literal[False] = False


def _ref(record: d.Artifact) -> d.Ref:
    return d.Ref(id=record.id, project_id=record.project_id, snapshot_id=record.snapshot_id)


def _stable_id(prefix: str, project_id: str, snapshot_id: str, *parts: object) -> str:
    payload = json.dumps(
        [project_id, snapshot_id, *parts], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return f"{prefix}.{hashlib.sha256(payload.encode()).hexdigest()[:24]}"


def _model_hash(model: d.ProjectModel) -> str:
    payload = json.dumps(
        model.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def deterministic_pairwise(
    dimensions: Mapping[str, Sequence[str]], max_combinations: int
) -> list[dict[str, str]]:
    """Return a stable bounded greedy pair-covering set; never defaults to Cartesian output."""

    normalized = {key: sorted(set(values)) for key, values in sorted(dimensions.items()) if values}
    if not normalized:
        return []
    keys = list(normalized)
    if len(keys) == 1:
        return [{keys[0]: value} for value in normalized[keys[0]][:max_combinations]]
    selected: list[dict[str, str]] = []
    seen: set[tuple[tuple[str, str], ...]] = set()
    defaults = {key: normalized[key][0] for key in keys}
    for left_index, left in enumerate(keys):
        for right in keys[left_index + 1 :]:
            for left_value in normalized[left]:
                for right_value in normalized[right]:
                    candidate = {**defaults, left: left_value, right: right_value}
                    signature = tuple(candidate.items())
                    if signature not in seen:
                        selected.append(candidate)
                        seen.add(signature)
                    if len(selected) == max_combinations:
                        return selected
    return selected


def _unresolved_affected(model: d.ProjectModel) -> set[str]:
    affected: set[str] = set()
    for node in model.nodes:
        if isinstance(node, d.Conflict) and node.status == "unresolved":
            affected.update(ref.id for ref in node.affected + node.conflicting_claims)
        elif isinstance(node, d.Ambiguity) and node.status == "open":
            affected.update(ref.id for ref in node.affected)
    return affected


def _oracle_status(
    test: d.ExistingTest, index: int, model: d.ProjectModel, node_index: Mapping[str, d.Artifact]
) -> OracleSupportFinding:
    oracle_ref = test.oracle_ids[index] if index < len(test.oracle_ids) else None
    status: OracleSupportStatus
    evidence: list[d.Ref] = []
    if model.ledger.manifest.completeness not in {"COMPLETE", "SCOPED_COMPLETE"}:
        status, rationale = "BLOCKED_BY_SOURCE", "Required source completeness is insufficient."
    elif oracle_ref is None:
        status, rationale = "UNSUPPORTED", "Expected Result has no explicit oracle reference."
    else:
        oracle = node_index.get(oracle_ref.id)
        if not isinstance(oracle, d.Oracle):
            status, rationale = "UNSUPPORTED", "Oracle reference does not resolve."
        else:
            evidence = [oracle.claim]
            claim = node_index.get(oracle.claim.id)
            source = None
            if isinstance(claim, d.Claim) and claim.evidence:
                source = next(
                    (
                        item
                        for item in model.ledger.sources
                        if item.id == claim.evidence[0].source.id
                    ),
                    None,
                )
            if isinstance(source, d.Source) and source.lifecycle in {
                "superseded",
                "deprecated",
                "archived",
            }:
                status, rationale = "STALE", "Oracle depends on stale lifecycle evidence."
            elif isinstance(claim, d.Claim) and claim.conflict == "unresolved":
                status, rationale = (
                    "CONFLICTING",
                    "Oracle claim has unresolved conflicting evidence.",
                )
            elif not validate_oracle(oracle, model).valid:
                status, rationale = "UNSUPPORTED", "Oracle fails deterministic provenance policy."
            elif oracle.origin == "IMPLEMENTATION":
                status, rationale = (
                    "IMPLEMENTATION_DERIVED_ONLY",
                    "Oracle is valid characterization evidence, not contractual truth.",
                )
            elif "GROUPED_ORACLES" in test.quality_flags:
                status, rationale = (
                    "SUPPORTED_BUT_GROUPED",
                    "Explicit audit metadata marks grouped assertions.",
                )
            else:
                status, rationale = (
                    "SUPPORTED",
                    "Oracle resolves through current provenance policy.",
                )
    return OracleSupportFinding(
        id=_stable_id("oracle-finding", test.project_id, test.snapshot_id, test.id, index, status),
        project_id=test.project_id,
        snapshot_id=test.snapshot_id,
        test=_ref(test),
        oracle=oracle_ref,
        expected_result_index=index,
        status=status,
        rationale=rationale,
        evidence=evidence,
    )


def _signature(test: d.ExistingTest) -> tuple[object, ...]:
    return (
        test.objective,
        tuple(ref.id for ref in test.criterion_ids),
        test.layer,
        test.actor_id.id if test.actor_id else None,
        tuple(ref.id for ref in test.state_ids),
        tuple(ref.id for ref in test.channel_ids),
        test.data_partition,
        tuple(ref.id for ref in test.risk_ids),
        tuple(ref.id for ref in test.oracle_ids),
    )


def analyze_project(
    model: d.ProjectModel, config: AnalysisConfig | None = None
) -> M2AnalysisReport:
    """Analyze explicit M1 evidence without semantic guessing or historical mutation."""

    config = config or AnalysisConfig()
    if model.ledger.manifest.mode == "REGRESSION_AUDIT":
        raise ValueError("M6 regression/change-impact mode is outside M2")
    mode = cast(AuditMode, model.ledger.manifest.mode)
    validation = validate_project_model(model)
    scope_ok = model.ledger.manifest.completeness in {"COMPLETE", "SCOPED_COMPLETE"}
    node_index = artifacts(model)
    requirements = sorted(
        (node for node in model.nodes if isinstance(node, d.Requirement)), key=lambda item: item.id
    )
    atoms = sorted(
        (node for node in model.nodes if isinstance(node, d.AtomicCriterion)),
        key=lambda item: item.id,
    )
    tests = sorted(
        (node for node in model.nodes if isinstance(node, d.ExistingTest)), key=lambda item: item.id
    )
    history_summary = history_patterns(model)
    affected = _unresolved_affected(model)
    atomicity: list[AtomicityResult] = []
    findings: list[AuditFinding] = []
    proposals: list[ImprovementProposal] = []
    edges: list[TraceabilityEdge] = []

    def proposal(
        asset: d.Ref | None, kind: ProposalKind, rationale: str, related: list[d.Ref]
    ) -> None:
        proposals.append(
            ImprovementProposal(
                id=_stable_id(
                    "proposal.m2",
                    model.project_id,
                    model.snapshot_id,
                    asset.id if asset else "project",
                    kind,
                    rationale,
                ),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                asset=asset,
                kind=kind,
                rationale=rationale,
                related=related,
            )
        )

    atoms_by_requirement: dict[str, list[d.AtomicCriterion]] = defaultdict(list)
    for atom in atoms:
        atoms_by_requirement[atom.requirement.id].append(atom)
        edges.append(
            TraceabilityEdge(
                id=_stable_id(
                    "edge",
                    model.project_id,
                    model.snapshot_id,
                    atom.requirement.id,
                    atom.id,
                    "has_atom",
                ),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                source=atom.requirement,
                target=_ref(atom),
                relation="REQUIREMENT_HAS_ATOM",
                evidence=atom.claims,
            )
        )
    for requirement in requirements:
        explicit = atoms_by_requirement[requirement.id]
        conflict = requirement.id in affected or any(atom.id in affected for atom in explicit)
        atomicity_status: AtomicityStatus = (
            "CONFLICTING" if conflict else "EXPLICIT" if explicit else "NO_EXPLICIT_ATOMS"
        )
        rationale = (
            "Requirement or criterion evidence is conflicting."
            if conflict
            else "Explicit criterion atoms are present."
            if explicit
            else "No explicit atom exists; natural-language decomposition was not guessed."
        )
        atomicity.append(
            AtomicityResult(
                id=_stable_id("atomicity", model.project_id, model.snapshot_id, requirement.id),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                requirement=_ref(requirement),
                atoms=[_ref(atom) for atom in explicit],
                status=atomicity_status,
                rationale=rationale,
                evidence=requirement.claims,
                review_required=atomicity_status != "EXPLICIT",
            )
        )
        if not explicit:
            findings.append(
                AuditFinding(
                    id=_stable_id(
                        "finding", model.project_id, model.snapshot_id, requirement.id, "atomicity"
                    ),
                    project_id=model.project_id,
                    snapshot_id=model.snapshot_id,
                    asset=_ref(requirement),
                    kind="REQUIREMENT_NOT_ATOMIZED",
                    rationale=rationale,
                    supporting_evidence=requirement.claims,
                    impacted=[_ref(requirement)],
                    severity="MEDIUM",
                    confidence="DETERMINISTIC",
                    proposed_action="Request explicit atomic acceptance criteria.",
                    human_clarification_required=True,
                )
            )

    oracle_findings = [
        _oracle_status(test, index, model, node_index)
        for test in tests
        for index in range(len(test.expected_results))
    ]
    oracle_by_test: dict[str, list[OracleSupportFinding]] = defaultdict(list)
    for item in oracle_findings:
        oracle_by_test[item.test.id].append(item)

    classifications: dict[str, AssetClassification] = {}
    for test in tests:
        linked = {ref.id for ref in test.requirement_ids + test.criterion_ids}
        stale_lifecycles = {
            candidate.lifecycle
            for identifier in linked
            if (candidate := node_index.get(identifier)) is not None
            and isinstance(candidate, d.Requirement)
        }
        path_nodes = [node_index.get(path.id) for path in test.path_ids]
        path_verified = bool(path_nodes) and all(
            isinstance(path_node, d.VerifiedPath) and path_node.verification_status == "verified"
            for path_node in path_nodes
        )
        conflict = bool(linked & affected)
        unsupported = any(
            item.status not in {"SUPPORTED", "SUPPORTED_BUT_GROUPED", "IMPLEMENTATION_DERIVED_ONLY"}
            for item in oracle_by_test[test.id]
        )
        if not scope_ok:
            classification: AssetClassification = "BLOCKED_BY_SOURCE"
        elif conflict or "CONFLICTING_EXPECTED_RESULT" in test.quality_flags:
            classification = "CONFLICTING"
        elif "deprecated" in stale_lifecycles:
            classification = "OBSOLETE_CANDIDATE"
        elif "superseded" in stale_lifecycles:
            classification = "STALE"
        elif not linked:
            classification = "UNTRACEABLE"
        elif not test.actions or not path_verified:
            classification = "NON_EXECUTABLE"
        elif "AMBIGUOUS_ACTION" in test.quality_flags or "AMBIGUOUS_RESULT" in test.quality_flags:
            classification = "AMBIGUOUS"
        elif unsupported or not test.expected_results:
            classification = "AMBIGUOUS"
        elif test.requirement_ids and not test.criterion_ids:
            classification = "PARTIAL_COVERAGE"
        elif (
            not test.preconditions
            or not test.cleanup
            or test.data_partition is None
            or test.actor_id is None
            or test.environment is None
            or "GROUPED_ORACLES" in test.quality_flags
            or ("MEASUREMENT_SENSITIVE" in test.quality_flags and not test.measurement_protocol)
        ):
            classification = "VALID_WITH_IMPROVEMENT"
        else:
            classification = "VALID_AS_IS"
        classifications[test.id] = classification

    signature_groups: dict[tuple[object, ...], list[d.ExistingTest]] = defaultdict(list)
    for test in tests:
        execution_signature = tuple(sorted(history_summary.get(test.id, {}).items()))
        signature_groups[(*_signature(test), execution_signature)].append(test)
    for group in signature_groups.values():
        if len(group) < 2 or group[0].objective is None:
            continue
        for test in sorted(group, key=lambda item: item.id)[1:]:
            classifications[test.id] = (
                "DUPLICATE_INTENTIONAL" if test.intentional_regression else "DUPLICATE_REDUNDANT"
            )

    for test in tests:
        classification = classifications[test.id]
        rationale = {
            "VALID_AS_IS": "Explicit audit facts satisfy the implemented M2 checks.",
            "VALID_WITH_IMPROVEMENT": (
                "The test is traceable but has explicit execution-quality gaps."
            ),
            "PARTIAL_COVERAGE": "The test links a requirement but no explicit criterion atom.",
            "AMBIGUOUS": "Action/result or oracle evidence is explicitly ambiguous or unsupported.",
            "BLOCKED_BY_SOURCE": "Incomplete required evidence prevents a conclusive audit.",
            "DUPLICATE_INTENTIONAL": (
                "Exact behavioral signature is duplicated and marked intentional regression."
            ),
            "DUPLICATE_REDUNDANT": (
                "Exact behavioral signature is duplicated without an intentional-regression marker."
            ),
            "CONFLICTING": "An unresolved conflict affects linked evidence.",
            "STALE": "The test links a superseded or deprecated requirement.",
            "OBSOLETE_CANDIDATE": "The test is a non-destructive obsolete review candidate.",
            "UNTRACEABLE": "No explicit requirement or criterion link exists.",
            "NON_EXECUTABLE": "Explicit actions or verified path references are absent.",
        }[classification]
        findings.append(
            AuditFinding(
                id=_stable_id(
                    "finding", model.project_id, model.snapshot_id, test.id, classification
                ),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                asset=_ref(test),
                classification=classification,
                kind="EXISTING_TEST_AUDIT",
                rationale=rationale,
                supporting_evidence=test.claims,
                impacted=test.requirement_ids + test.criterion_ids + test.risk_ids,
                severity="INFO" if classification == "VALID_AS_IS" else "MEDIUM",
                confidence="DETERMINISTIC",
                proposed_action=(
                    "Preserve the historical asset and review the non-destructive finding."
                ),
                human_clarification_required=classification
                in {"AMBIGUOUS", "BLOCKED_BY_SOURCE", "CONFLICTING"},
            )
        )
        if not test.preconditions:
            proposal(
                _ref(test),
                "IMPROVE_PRECONDITIONS",
                "Explicit preconditions are absent.",
                test.criterion_ids,
            )
        if not test.cleanup:
            proposal(
                _ref(test),
                "ADD_CLEANUP",
                "Cleanup/isolation evidence is absent.",
                test.criterion_ids,
            )
        if not linked:
            proposal(_ref(test), "ADD_TRACEABILITY", "Add an evidence-backed criterion link.", [])
        if "GROUPED_ORACLES" in test.quality_flags:
            proposal(
                _ref(test),
                "SPLIT_GROUPED_ORACLE",
                "Separate explicitly grouped assertions.",
                test.oracle_ids,
            )
        if "HARD_CODED_DATA" in test.quality_flags:
            proposal(
                _ref(test),
                "PARAMETERIZE_DATA",
                "Replace hard-coded test data with an evidence-backed parameter candidate.",
                [],
            )
        elif test.data_partition is None:
            proposal(
                _ref(test),
                "PARAMETERIZE_DATA",
                "Explicit test-data properties or partitions are absent.",
                test.criterion_ids,
            )
        if "REPEATED_PREPARATION" in test.quality_flags:
            proposal(
                _ref(test),
                "SHARED_STEP_CANDIDATE",
                "Review repeated preparation as a Shared Step candidate.",
                [],
            )

    atom_tests: dict[str, list[d.ExistingTest]] = defaultdict(list)
    nominal_requirements: set[str] = set()
    for test in tests:
        nominal_requirements.update(ref.id for ref in test.requirement_ids)
        for atom_ref in test.criterion_ids:
            atom_tests[atom_ref.id].append(test)
            linked_atom = node_index.get(atom_ref.id)
            if isinstance(linked_atom, d.AtomicCriterion):
                nominal_requirements.add(linked_atom.requirement.id)
        relationships = [
            *((ref, "REQUIREMENT_NOMINALLY_LINKED_TO_TEST") for ref in test.requirement_ids),
            *((ref, "ATOM_COVERED_BY_TEST") for ref in test.criterion_ids),
            *((ref, "STATE_COVERED_BY_TEST") for ref in test.state_ids),
            *((ref, "CHANNEL_COVERED_BY_TEST") for ref in test.channel_ids),
            *((ref, "RISK_COVERED_BY_TEST") for ref in test.risk_ids),
            *((ref, "TEST_USES_ORACLE") for ref in test.oracle_ids),
        ]
        if test.actor_id:
            relationships.append((test.actor_id, "ACTOR_COVERED_BY_TEST"))
        for source, relation in relationships:
            edges.append(
                TraceabilityEdge(
                    id=_stable_id(
                        "edge", model.project_id, model.snapshot_id, source.id, test.id, relation
                    ),
                    project_id=model.project_id,
                    snapshot_id=model.snapshot_id,
                    source=source,
                    target=_ref(test),
                    relation=relation,  # type: ignore[arg-type]
                    evidence=test.claims,
                )
            )

    coverage_atoms: list[AtomCoverage] = []
    for atom in atoms:
        linked_tests = atom_tests[atom.id]
        requirement_nominal = atom.requirement.id in nominal_requirements
        if atom.id in affected or atom.requirement.id in affected:
            state: CoverageState = "CONFLICTING"
            rationale = "Unresolved evidence conflict prevents a coverage conclusion."
        elif not scope_ok:
            state, rationale = "BLOCKED_UNKNOWN", "Required source completeness is insufficient."
        elif any(classifications[test.id] == "VALID_AS_IS" for test in linked_tests):
            state, rationale = (
                "BEHAVIORALLY_COVERED",
                "An executable test explicitly covers this atom with supported oracle evidence.",
            )
        elif linked_tests:
            state, rationale = (
                "PARTIALLY_COVERED",
                "Direct atom links exist, but test audit gaps prevent full behavioral coverage.",
            )
        elif requirement_nominal:
            state, rationale = (
                "NOMINALLY_LINKED",
                "The parent requirement is linked, but this atom is not directly covered.",
            )
        else:
            state, rationale = "UNCOVERED", "No explicit test link covers this atom."
        coverage_atoms.append(
            AtomCoverage(
                id=_stable_id("coverage", model.project_id, model.snapshot_id, atom.id),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                requirement=atom.requirement,
                atom=_ref(atom),
                tests=[_ref(test) for test in linked_tests],
                state=state,
                rationale=rationale,
            )
        )
        if state in {"UNCOVERED", "NOMINALLY_LINKED", "PARTIALLY_COVERED"}:
            proposal(None, "ADD_COVERAGE", rationale, [_ref(atom)])

    risks: list[RiskAnalysisRecord] = []
    scenarios: list[ScenarioRecord] = []
    scenario_keys: set[tuple[object, ...]] = set()

    def add_scenario(**values: object) -> None:
        key = tuple(sorted((key, str(value)) for key, value in values.items()))
        if key in scenario_keys:
            return
        scenario_keys.add(key)
        scenarios.append(
            ScenarioRecord(
                id=_stable_id("scenario.m2", model.project_id, model.snapshot_id, key),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                **values,  # type: ignore[arg-type]
            )
        )

    for atom in atoms:
        parent_requirement = node_index.get(atom.requirement.id)
        origin: d.Origin = "CONTRACT"
        if atom.claims:
            claim = node_index.get(atom.claims[0].id)
            if isinstance(claim, d.Claim):
                origin = claim.origin
        supported_oracle: d.Ref | None = None
        for linked_test in atom_tests.get(atom.id, []):
            supported = next(
                (
                    item
                    for item in oracle_by_test[linked_test.id]
                    if item.status in {"SUPPORTED", "IMPLEMENTATION_DERIVED_ONLY"}
                    and item.oracle is not None
                ),
                None,
            )
            if supported is not None:
                supported_oracle = supported.oracle
                break
        dimensions = {
            "actor": [ref.id for ref in atom.actors],
            "state": [ref.id for ref in atom.states],
            "channel": [ref.id for ref in atom.channels],
        }
        combinations = deterministic_pairwise(dimensions, config.max_pairwise_combinations)
        if not combinations:
            combinations = [{}]
        for combination in combinations:
            add_scenario(
                origin=origin,
                technique="PAIRWISE" if len(dimensions) > 1 and combination else "CRITERION",
                source_requirement=(
                    _ref(parent_requirement)
                    if isinstance(parent_requirement, d.Requirement)
                    else atom.requirement
                ),
                source_atom=_ref(atom),
                actor=_ref(node_index[combination["actor"]]) if "actor" in combination else None,
                pre_state=_ref(node_index[combination["state"]])
                if "state" in combination
                else None,
                channel=_ref(node_index[combination["channel"]])
                if "channel" in combination
                else None,
                oracle=supported_oracle,
                rationale="Explicit criterion dimensions form a bounded scenario candidate.",
                readiness="READY_FOR_M3" if supported_oracle else "REVIEW_REQUIRED",
            )
        for boundary_ref in atom.boundaries:
            boundary = node_index.get(boundary_ref.id)
            if not isinstance(boundary, d.Constraint):
                continue
            for partition in boundary.partitions:
                add_scenario(
                    origin=origin,
                    technique="EQUIVALENCE_PARTITION",
                    source_requirement=atom.requirement,
                    source_atom=_ref(atom),
                    data_partition=partition,
                    rationale="Partition is explicitly declared by a referenced constraint.",
                    readiness="REVIEW_REQUIRED",
                )
            if boundary.value_type in {"integer", "number", "length", "cardinality"}:
                values: set[int | float] = set()
                for limit in (boundary.minimum, boundary.maximum):
                    if limit is not None:
                        values.update({limit - 1, limit, limit + 1})
                for value in sorted(values):
                    if boundary.value_type in {"length", "cardinality"} and value < 0:
                        continue
                    add_scenario(
                        origin=origin,
                        technique="BOUNDARY_VALUE",
                        source_requirement=atom.requirement,
                        source_atom=_ref(atom),
                        constraint_values=[str(value)],
                        rationale="Candidate value is adjacent to an explicit numeric limit.",
                        readiness="REVIEW_REQUIRED",
                    )

    for transition in sorted(
        (node for node in model.nodes if isinstance(node, d.Transition)), key=lambda item: item.id
    ):
        claim = node_index.get(transition.claims[0].id) if transition.claims else None
        origin = claim.origin if isinstance(claim, d.Claim) else "EXPLORATORY"
        add_scenario(
            origin=origin,
            technique="STATE_TRANSITION",
            pre_state=transition.from_state,
            stimulus=transition.trigger,
            actor=transition.actors[0] if transition.actors else None,
            channel=transition.channels[0] if transition.channels else None,
            rationale=(
                "Scenario reflects an explicit modeled transition; no invalid outcome is inferred."
            ),
            readiness="REVIEW_REQUIRED",
        )

    for rule in sorted(
        (node for node in model.nodes if isinstance(node, d.DecisionRule)), key=lambda item: item.id
    ):
        rule_claim = node_index.get(rule.claims[0].id) if rule.claims else None
        add_scenario(
            origin=rule_claim.origin if isinstance(rule_claim, d.Claim) else "EXPLORATORY",
            technique="DECISION_TABLE",
            stimulus=rule.action,
            constraint_values=[ref.id for ref in rule.conditions],
            rationale="Scenario reflects an explicit structured condition/outcome rule.",
            readiness="REVIEW_REQUIRED",
        )

    severity_rank = {name: index + 1 for index, name in enumerate(config.risk_scale)}
    for risk in sorted(
        (node for node in model.nodes if isinstance(node, d.Risk)), key=lambda item: item.id
    ):
        rank = severity_rank.get(risk.severity.lower())
        record = RiskAnalysisRecord(
            id=_stable_id("risk-analysis", model.project_id, model.snapshot_id, risk.id),
            project_id=model.project_id,
            snapshot_id=model.snapshot_id,
            source_risk=_ref(risk),
            category=risk.category,
            affected=risk.affected,
            evidence=risk.claims,
            rationale=risk.derivation,
            impact=risk.severity,
            rank=rank,
            review_required=rank is None or not risk.claims,
        )
        risks.append(record)
        add_scenario(
            origin="RISK",
            technique="RISK_PACK",
            source_risk=_ref(risk),
            rationale=(
                "An explicitly modeled risk activates only its named category; "
                "no outcome is invented."
            ),
            readiness="EXPLORATORY",
        )
        proposal(
            None,
            "ADD_RISK_SCENARIO",
            "Review an explicit risk-derived exploratory scenario.",
            [_ref(risk)],
        )

    scenario_risk_rank = {risk.source_risk.id: risk.rank or 0 for risk in risks}
    ordered = sorted(
        scenarios,
        key=lambda scenario: (
            -scenario_risk_rank.get(scenario.source_risk.id if scenario.source_risk else "", 0),
            scenario.technique != "BOUNDARY_VALUE",
            scenario.id,
        ),
    )
    selected_ids = {scenario.id for scenario in ordered[: config.max_scenarios]}
    dispositions = [
        ScenarioDisposition(
            id=_stable_id("disposition", model.project_id, model.snapshot_id, scenario.id),
            project_id=model.project_id,
            snapshot_id=model.snapshot_id,
            scenario=_ref(scenario),
            disposition=(
                "EXPLORATORY"
                if scenario.readiness == "EXPLORATORY"
                else "BLOCKED"
                if scenario.readiness == "BLOCKED"
                else "SELECTED"
                if scenario.id in selected_ids
                else "DEFERRED"
            ),
            rationale=(
                "Risk lacks a defensible oracle and remains exploratory."
                if scenario.readiness == "EXPLORATORY"
                else "Selected within the configured deterministic bound."
                if scenario.id in selected_ids
                else "Deferred by the configured scenario bound; retained in the universe."
            ),
        )
        for scenario in ordered
    ]

    clone_classifications: dict[str, CloneClassification] = {}
    if mode == "CLONE_REUSE":
        mapping: dict[AssetClassification, CloneClassification] = {
            "VALID_AS_IS": "REUSABLE",
            "VALID_WITH_IMPROVEMENT": "REQUIRES_UPDATE",
            "PARTIAL_COVERAGE": "REQUIRES_UPDATE",
            "AMBIGUOUS": "UNKNOWN",
            "BLOCKED_BY_SOURCE": "UNKNOWN",
            "DUPLICATE_INTENTIONAL": "DUPLICATE",
            "DUPLICATE_REDUNDANT": "DUPLICATE",
            "CONFLICTING": "CONFLICTING",
            "STALE": "OBSOLETE_CANDIDATE",
            "OBSOLETE_CANDIDATE": "OBSOLETE_CANDIDATE",
            "UNTRACEABLE": "UNKNOWN",
            "NON_EXECUTABLE": "REQUIRES_UPDATE",
        }
        clone_classifications = {test.id: mapping[classifications[test.id]] for test in tests}

    for test_id, counts in history_summary.items():
        history_test = node_index.get(test_id)
        if not isinstance(history_test, d.ExistingTest):
            continue
        for outcome, kind in (("FAIL", "REPEATED_FAIL"), ("BLOCKED", "REPEATED_BLOCKED")):
            if counts.get(outcome, 0) < 2:
                continue
            findings.append(
                AuditFinding(
                    id=_stable_id(
                        "finding", model.project_id, model.snapshot_id, history_test.id, kind
                    ),
                    project_id=model.project_id,
                    snapshot_id=model.snapshot_id,
                    asset=_ref(history_test),
                    kind=kind,
                    rationale=(
                        f"Execution history contains {counts[outcome]} explicit {outcome} results; "
                        "history is operational evidence, not contract."
                    ),
                    supporting_evidence=history_test.claims,
                    impacted=history_test.criterion_ids + history_test.risk_ids,
                    severity="MEDIUM",
                    confidence="DETERMINISTIC",
                    proposed_action="Review the preserved execution history and current evidence.",
                    human_clarification_required=False,
                )
            )

    limitations = []
    if not scope_ok:
        limitations.append(
            "Required source evidence is incomplete; no full audit certainty is claimed."
        )
    if any(item.status == "NO_EXPLICIT_ATOMS" for item in atomicity):
        limitations.append("Requirements without explicit atoms were not decomposed from prose.")
    if mode == "GREENFIELD" and not tests:
        limitations.append(
            "No historical tests exist; asset-defect classifications were not fabricated."
        )
    if validation.issues:
        limitations.append("The input Project Model has deterministic integrity issues.")
    coverage = CoverageReport(
        id="coverage-report",
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        atoms=sorted(coverage_atoms, key=lambda item: item.atom.id),
        nominal_linked_requirements=len(nominal_requirements & {item.id for item in requirements}),
        total_requirements=len(requirements),
        behaviorally_covered_atoms=sum(
            item.state == "BEHAVIORALLY_COVERED" for item in coverage_atoms
        ),
        total_explicit_atoms=len(atoms),
        denominator_reliable=scope_ok and all(item.status == "EXPLICIT" for item in atomicity),
        limitation=None if scope_ok else "Counts are reported without a completeness percentage.",
    )
    analysis_status: Literal["COMPLETE", "PARTIAL", "INVALID"] = (
        "INVALID"
        if not validation.valid
        else "COMPLETE"
        if scope_ok and coverage.denominator_reliable
        else "PARTIAL"
    )
    return M2AnalysisReport(
        id="m2-analysis-report",
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        mode=mode,
        status=analysis_status,
        source_completeness=model.ledger.manifest.completeness,
        atomicity=sorted(atomicity, key=lambda item: item.requirement.id),
        traceability=sorted(edges, key=lambda item: item.id),
        coverage=coverage,
        findings=sorted(findings, key=lambda item: item.id),
        oracle_findings=sorted(oracle_findings, key=lambda item: item.id),
        history_summary=history_summary,
        clone_classifications=dict(sorted(clone_classifications.items())),
        risks=sorted(risks, key=lambda item: item.id),
        scenarios=sorted(scenarios, key=lambda item: item.id),
        dispositions=sorted(dispositions, key=lambda item: item.id),
        proposals=sorted(proposals, key=lambda item: item.id),
        limitations=sorted(set(limitations)),
        input_model_hash=_model_hash(model),
    )


def validate_analysis_report(report: M2AnalysisReport, model: d.ProjectModel) -> Result:
    """Mechanically validate M2 scope, references, and non-destructive invariants."""

    result = Result()
    if (report.project_id, report.snapshot_id) != (model.project_id, model.snapshot_id):
        result.add("SCOPE_NAMESPACE", report, "M2 report and Project Model namespaces differ.")
    if report.input_model_hash != _model_hash(model):
        result.add(
            "M2_STALE_INPUT", report, "M2 report does not bind to the current Project Model."
        )
    if (report.coverage.project_id, report.coverage.snapshot_id) != (
        model.project_id,
        model.snapshot_id,
    ):
        result.add("SCOPE_NAMESPACE", report.coverage, "Coverage is outside the input namespace.")
    model_artifacts = artifacts(model)
    known = set(model_artifacts)
    known.update(
        record.id
        for collection in (
            report.atomicity,
            report.traceability,
            report.coverage.atoms,
            report.findings,
            report.oracle_findings,
            report.risks,
            report.scenarios,
            report.dispositions,
            report.proposals,
        )
        for record in collection
    )
    known.add(report.coverage.id)
    report_records = (
        *report.atomicity,
        *report.traceability,
        *report.coverage.atoms,
        *report.findings,
        *report.oracle_findings,
        *report.risks,
        *report.scenarios,
        *report.dispositions,
        *report.proposals,
    )
    for record in report_records:
        if (record.project_id, record.snapshot_id) != (model.project_id, model.snapshot_id):
            result.add("SCOPE_NAMESPACE", record, "M2 artifact is outside the input namespace.")
        for field_name in type(record).model_fields:
            value = getattr(record, field_name)
            references = (
                [value] if isinstance(value, d.Ref) else value if isinstance(value, list) else []
            )
            for reference in references:
                if isinstance(reference, d.Ref) and (
                    reference.id not in known
                    or (reference.project_id, reference.snapshot_id)
                    != (model.project_id, model.snapshot_id)
                ):
                    result.add(
                        "M2_INVALID_REF", record, "M2 relationship is missing or crosses namespace."
                    )
    for identifier in set(report.history_summary) | set(report.clone_classifications):
        if not isinstance(model_artifacts.get(identifier), d.ExistingTest):
            result.add(
                "M2_INVALID_REF",
                report,
                "History or clone classification does not identify an existing test.",
            )
    if report.external_writes or report.historical_assets_mutated:
        result.add("M2_DESTRUCTIVE", report, "M2 must be read-only and preserve historical assets.")
    if report.status == "COMPLETE" and (
        model.ledger.manifest.completeness not in {"COMPLETE", "SCOPED_COMPLETE"}
        or not report.coverage.denominator_reliable
    ):
        result.add(
            "M2_FALSE_COMPLETE", report, "Incomplete evidence cannot yield COMPLETE M2 status."
        )
    return result


def history_patterns(model: d.ProjectModel) -> dict[str, dict[str, int]]:
    """Return stable operational counts; Pass is never interpreted as contract evidence."""

    counts: dict[str, Counter[str]] = defaultdict(Counter)
    for node in model.nodes:
        if isinstance(node, d.ExistingResult) and node.test is not None:
            counts[node.test.id][node.outcome] += 1
    return {
        identifier: dict(sorted(values.items())) for identifier, values in sorted(counts.items())
    }
