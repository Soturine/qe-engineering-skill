"""Typed M3 authoring contracts.

The contracts deliberately separate unresolved authoring proposals from strict
``TestCase`` artifacts. Generation and trust validation are implemented in later
M3 stages; these records perform shape, readiness, and scope checks only.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from qe_skill import domain as d
from qe_skill.integrity import artifacts, validate_project_model, validate_test_case
from qe_skill.m2 import M2AnalysisReport, ScenarioRecord, validate_analysis_report
from qe_skill.validation import Result, validate_claim, validate_oracle

GenerationMode = Literal["GREENFIELD", "BROWNFIELD", "CLONE_REUSE"]
ProposalAction = Literal["NEW", "KEEP", "IMPROVE", "REVISE", "REPLACE"]
ReviewStatus = Literal["NOT_REQUIRED", "REVIEW_REQUIRED", "APPROVED", "REJECTED"]
DiffKind = Literal["ADDED", "REMOVED", "CHANGED", "UNCHANGED"]
OracleMaterializationStatus = Literal[
    "MATERIALIZED_NORMATIVE",
    "MATERIALIZED_CHARACTERIZATION",
    "EXPLORATORY_ONLY",
    "BLOCKED_SOURCE",
    "CONFLICTING",
    "UNSUPPORTED",
]


def _records(value: object) -> Iterator[BaseModel]:
    if isinstance(value, BaseModel):
        yield value
        for field_value in value.__dict__.values():
            yield from _records(field_value)
    elif isinstance(value, list | tuple):
        for item in value:
            yield from _records(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _records(item)


def _require_scope(owner: d.Artifact) -> None:
    for record in _records(owner):
        if record is owner:
            continue
        if isinstance(record, d.Artifact | d.Ref) and (
            record.project_id != owner.project_id or record.snapshot_id != owner.snapshot_id
        ):
            raise ValueError(f"cross-scope reference or artifact: {record.id}")


class GenerationInputBinding(d.Record):
    project_model_hash: d.Digest
    m2_analysis_hash: d.Digest
    generator_version: d.Text
    schema_version: Literal["1.0"] = "1.0"
    configuration_hash: d.Digest


class OracleMaterialization(d.Record):
    status: OracleMaterializationStatus
    oracle: d.Oracle | None = None
    rationale: d.Text
    source_claim: d.Ref | None = None


class AuthoringConfig(d.Record):
    generator_version: d.Text = "0.3.0"
    generated_at: d.Timestamp = "1970-01-01T00:00:00Z"
    max_cases: int = Field(default=100, ge=1, le=10_000)
    environment_claim: d.Ref | None = None
    cleanup_claim: d.Ref | None = None
    isolation_claim: d.Ref | None = None
    build: str | None = None
    profile: str | None = None


def canonical_hash(value: BaseModel | dict[str, object]) -> str:
    payload = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def stable_id(prefix: str, project_id: str, snapshot_id: str, *parts: object) -> str:
    payload = {"scope": [project_id, snapshot_id], "parts": list(parts)}
    return f"{prefix}.{canonical_hash(payload)[:24]}"


def materialize_oracle(
    claim_ref: d.Ref,
    model: d.ProjectModel,
    *,
    expected_text: str | None = None,
) -> OracleMaterialization:
    """Create only the oracle semantics already supported by an exact current claim."""

    claim = next((item for item in model.claims if item.id == claim_ref.id), None)
    if (
        claim is None
        or claim_ref.project_id != model.project_id
        or claim_ref.snapshot_id != model.snapshot_id
    ):
        return OracleMaterialization(
            status="BLOCKED_SOURCE",
            rationale="The source claim is missing or outside the current project snapshot.",
            source_claim=claim_ref,
        )
    claim_result = validate_claim(claim, model)
    if not claim_result.valid:
        status: OracleMaterializationStatus = (
            "CONFLICTING"
            if any(issue.code == "PROV_CONFLICT" for issue in claim_result.issues)
            else "BLOCKED_SOURCE"
        )
        return OracleMaterialization(
            status=status,
            rationale="The current claim does not pass provenance validation.",
            source_claim=claim_ref,
        )
    if expected_text is not None and expected_text != claim.statement:
        return OracleMaterialization(
            status="UNSUPPORTED",
            rationale="Expected Result text must exactly preserve the supporting claim.",
            source_claim=claim_ref,
        )
    normative = claim.origin in {"CONTRACT", "ORGANIZATIONAL_POLICY"} and not claim.inferred
    if claim.origin == "IMPLEMENTATION":
        status = "MATERIALIZED_CHARACTERIZATION"
        usage: Literal["acceptance", "characterization", "exploration"] = "characterization"
    elif normative:
        status = "MATERIALIZED_NORMATIVE"
        usage = "acceptance"
    else:
        status = "EXPLORATORY_ONLY"
        usage = "exploration"
    oracle = d.Oracle(
        id=stable_id("m3.oracle", model.project_id, model.snapshot_id, claim.id, status),
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        statement=claim.statement,
        origin=claim.origin,
        claim=claim_ref,
        normative=normative,
        inferred=claim.inferred,
        confidence=claim.confidence,
        usage=usage,
    )
    check_model = model.model_copy(deep=True)
    check_model.oracles.append(oracle)
    if not validate_oracle(oracle, check_model).valid:
        return OracleMaterialization(
            status="UNSUPPORTED",
            rationale="The candidate oracle did not pass the repository trust validator.",
            source_claim=claim_ref,
        )
    return OracleMaterialization(
        status=status,
        oracle=oracle,
        rationale="Oracle semantics exactly preserve the validated current claim.",
        source_claim=claim_ref,
    )


def reuse_oracle(oracle_ref: d.Ref, model: d.ProjectModel) -> OracleMaterialization:
    oracle = next((item for item in model.oracles if item.id == oracle_ref.id), None)
    if (
        oracle is None
        or oracle_ref.project_id != model.project_id
        or oracle_ref.snapshot_id != model.snapshot_id
    ):
        return OracleMaterialization(
            status="BLOCKED_SOURCE",
            rationale="Oracle reuse requires an oracle in the exact current project snapshot.",
        )
    if not validate_oracle(oracle, model).valid:
        return OracleMaterialization(
            status="UNSUPPORTED",
            rationale="The existing oracle does not pass current provenance validation.",
            source_claim=oracle.claim,
        )
    if oracle.normative:
        status: OracleMaterializationStatus = "MATERIALIZED_NORMATIVE"
    elif oracle.usage == "characterization":
        status = "MATERIALIZED_CHARACTERIZATION"
    else:
        status = "EXPLORATORY_ONLY"
    return OracleMaterialization(
        status=status,
        oracle=oracle,
        rationale="The existing oracle is current and passes provenance validation.",
        source_claim=oracle.claim,
    )


class DraftSupportedText(d.Record):
    text: str | None = None
    claims: list[d.Ref] = Field(default_factory=list)
    unresolved_reasons: list[d.Text] = Field(default_factory=list)


class DraftTestData(d.Record):
    name: d.Text
    properties: DraftSupportedText
    preparation: DraftSupportedText
    parameter_candidate: d.Ref | None = None


class DraftManualStep(d.Record):
    number: int = Field(ge=1)
    action: DraftSupportedText
    path: d.Ref | None = None
    oracle: d.Ref | None = None
    expected_result: str | None = None
    required: bool = True
    evidence_expectation: str | None = None
    blocking_reasons: list[d.Text] = Field(default_factory=list)


class FieldDiff(d.Record):
    field: d.Text
    kind: DiffKind
    before: str | None = None
    after: str | None = None
    rationale: d.Text
    evidence: list[d.Ref] = Field(default_factory=list)


class StepDiff(d.Record):
    kind: DiffKind
    original_step: int | None = Field(default=None, ge=1)
    proposed_step: int | None = Field(default=None, ge=1)
    rationale: d.Text
    evidence: list[d.Ref] = Field(default_factory=list)


class GeneratedCaseProposal(d.Artifact):
    action: ProposalAction
    title: d.Text
    objective: DraftSupportedText
    origin: d.Origin
    primary_provenance: list[d.Ref]
    requirements: list[d.Ref] = Field(default_factory=list)
    criteria: list[d.Ref] = Field(default_factory=list)
    risks: list[d.Ref] = Field(default_factory=list)
    scenarios: list[d.Ref] = Field(default_factory=list)
    priority_rationale: d.Text
    environment: DraftSupportedText
    build: str | None = None
    actor: d.Ref | None = None
    profile: str | None = None
    permissions: list[d.Ref] = Field(default_factory=list)
    preconditions: list[DraftSupportedText] = Field(default_factory=list)
    data: list[DraftTestData] = Field(default_factory=list)
    steps: list[DraftManualStep] = Field(default_factory=list)
    pass_rule: str | None = None
    fail_rule: str | None = None
    blocked_rule: d.Text
    cleanup: DraftSupportedText
    isolation: DraftSupportedText
    evidence_expectations: list[d.Text] = Field(default_factory=list)
    shared_step_candidates: list[d.Ref] = Field(default_factory=list)
    parameter_candidates: list[d.Ref] = Field(default_factory=list)
    readiness: d.Readiness
    blocking_notes: list[d.Text] = Field(default_factory=list)
    review_status: ReviewStatus
    rationale: d.Text
    materialized_test: d.TestCase | None = None
    proposal_only: Literal[True] = True

    @model_validator(mode="after")
    def validate_draft_boundary(self) -> GeneratedCaseProposal:
        _require_scope(self)
        if self.readiness == "READY":
            if self.materialized_test is None:
                raise ValueError("READY proposal requires a materialized TestCase")
            if self.blocking_notes:
                raise ValueError("READY proposal cannot retain blocking notes")
            unresolved = [
                text
                for text in [self.objective, self.environment, self.cleanup, self.isolation]
                if text.text is None or text.unresolved_reasons
            ]
            if unresolved:
                raise ValueError("READY proposal contains unresolved required text")
        return self


class TestRevisionProposal(d.Artifact):
    original_test: d.Ref
    action: Literal["KEEP", "IMPROVE", "REVISE", "REPLACE"]
    proposed_case: d.Ref | None = None
    field_diffs: list[FieldDiff] = Field(default_factory=list)
    step_diffs: list[StepDiff] = Field(default_factory=list)
    rationale: d.Text
    evidence: list[d.Ref]
    historical_asset_mutated: Literal[False] = False
    proposal_only: Literal[True] = True

    @model_validator(mode="after")
    def validate_scope(self) -> TestRevisionProposal:
        _require_scope(self)
        return self


class SharedStepCandidate(d.Artifact):
    title: d.Text
    steps: list[DraftManualStep] = Field(min_length=1)
    supporting_evidence: list[d.Ref]
    path_refs: list[d.Ref] = Field(default_factory=list)
    claim_refs: list[d.Ref] = Field(default_factory=list)
    used_by: list[d.Ref] = Field(min_length=2)
    rationale: d.Text
    readiness: d.Readiness
    review_status: ReviewStatus

    @model_validator(mode="after")
    def validate_scope(self) -> SharedStepCandidate:
        _require_scope(self)
        return self


class ParameterCandidate(d.Artifact):
    name: d.Text
    properties: DraftSupportedText
    constraints: list[d.Ref] = Field(default_factory=list)
    source_evidence: list[d.Ref]
    candidate_values: list[str] = Field(default_factory=list)
    used_by: list[d.Ref]
    rationale: d.Text

    @model_validator(mode="after")
    def validate_scope(self) -> ParameterCandidate:
        _require_scope(self)
        return self


class GenerationTraceabilityEdge(d.Artifact):
    source: d.Ref
    target: d.Ref
    relation: Literal[
        "REQUIREMENT_TO_CASE",
        "CRITERION_TO_CASE",
        "RISK_TO_CASE",
        "SCENARIO_TO_CASE",
        "POLICY_TO_CASE",
        "ORACLE_TO_STEP",
        "EXISTING_TEST_TO_REVISION",
        "CASE_TO_SHARED_STEP",
        "CASE_TO_PARAMETER",
    ]
    evidence: list[d.Ref]

    @model_validator(mode="after")
    def validate_scope(self) -> GenerationTraceabilityEdge:
        _require_scope(self)
        return self


class GenerationManifest(d.Artifact):
    mode: GenerationMode
    input_binding: GenerationInputBinding
    configuration: dict[str, str]
    artifact_refs: list[d.Ref]
    created_at: d.Timestamp
    tool_version: d.Text
    proposal_only: Literal[True] = True
    external_writes: Literal[False] = False

    @model_validator(mode="after")
    def validate_scope(self) -> GenerationManifest:
        _require_scope(self)
        return self


class M3GenerationReport(d.Artifact):
    mode: GenerationMode
    status: Literal["COMPLETE", "PARTIAL", "INVALID"]
    input_binding: GenerationInputBinding
    cases: list[GeneratedCaseProposal]
    test_model: d.TestModel
    revisions: list[TestRevisionProposal]
    shared_steps: list[SharedStepCandidate]
    parameters: list[ParameterCandidate]
    traceability: list[GenerationTraceabilityEdge]
    materialized_oracles: list[d.Oracle]
    manifest: GenerationManifest
    limitations: list[d.Text]
    proposal_only: Literal[True] = True
    external_writes: Literal[False] = False
    historical_assets_mutated: Literal[False] = False
    deterministic: Literal[True] = True

    @model_validator(mode="after")
    def validate_scope_and_binding(self) -> M3GenerationReport:
        _require_scope(self)
        if self.manifest.input_binding != self.input_binding:
            raise ValueError("manifest input binding differs from report binding")
        return self


def _ref(record: d.Artifact) -> d.Ref:
    return d.Ref(id=record.id, project_id=record.project_id, snapshot_id=record.snapshot_id)


def _claim_text(model: d.ProjectModel, refs: list[d.Ref]) -> DraftSupportedText:
    for claim_ref in refs:
        claim = next((item for item in model.claims if item.id == claim_ref.id), None)
        if claim is not None and validate_claim(claim, model).valid and not claim.inferred:
            return DraftSupportedText(text=claim.statement, claims=[claim_ref])
    return DraftSupportedText(
        unresolved_reasons=["No validated exact supporting claim is available."]
    )


def _configured_text(
    model: d.ProjectModel, claim_ref: d.Ref | None, missing: str
) -> DraftSupportedText:
    if claim_ref is None:
        return DraftSupportedText(unresolved_reasons=[missing])
    return _claim_text(model, [claim_ref])


def _scenario_path(
    scenario: ScenarioRecord, model: d.ProjectModel
) -> tuple[d.VerifiedPath | None, DraftSupportedText]:
    index = artifacts(model)
    channel = index.get(scenario.channel.id) if scenario.channel else None
    paths = sorted(
        (node for node in model.nodes if isinstance(node, d.VerifiedPath)), key=lambda node: node.id
    )
    for path in paths:
        if path.verification_status != "verified" or not path.steps:
            continue
        if isinstance(channel, d.Channel) and path.path_type != channel.channel_type:
            continue
        first = path.steps[0]
        return path, DraftSupportedText(text=first.instruction, claims=[first.claim])
    stimulus = index.get(scenario.stimulus.id) if scenario.stimulus else None
    claims = stimulus.claims if isinstance(stimulus, d.Action | d.Event) else []
    action = _claim_text(model, claims)
    action.unresolved_reasons.append("No verified operational path supports this action.")
    return None, action


def _case_from_scenario(
    scenario: ScenarioRecord,
    model: d.ProjectModel,
    config: AuthoringConfig,
) -> tuple[GeneratedCaseProposal, d.Oracle | None]:
    index = artifacts(model)
    atom = index.get(scenario.source_atom.id) if scenario.source_atom else None
    requirement = index.get(scenario.source_requirement.id) if scenario.source_requirement else None
    objective_refs = atom.claims if isinstance(atom, d.AtomicCriterion) else []
    if not objective_refs and isinstance(requirement, d.Requirement):
        objective_refs = requirement.claims
    objective = _claim_text(model, objective_refs)
    path, action = _scenario_path(scenario, model)
    oracle_result = reuse_oracle(scenario.oracle, model) if scenario.oracle else None
    if oracle_result is None and objective.claims:
        oracle_result = materialize_oracle(objective.claims[0], model)
    oracle = oracle_result.oracle if oracle_result else None
    exploratory = scenario.origin in {"RISK", "EXPLORATORY"} or (
        oracle is not None and not oracle.normative
    )
    blockers = list(action.unresolved_reasons + objective.unresolved_reasons)
    if oracle is None and not exploratory:
        blockers.append("No defensible normative oracle is available.")
    environment = _configured_text(
        model, config.environment_claim, "Environment evidence is not available."
    )
    cleanup = _configured_text(model, config.cleanup_claim, "Cleanup evidence is not available.")
    isolation = _configured_text(
        model, config.isolation_claim, "Isolation evidence is not available."
    )
    blockers.extend(environment.unresolved_reasons)
    blockers.extend(cleanup.unresolved_reasons)
    blockers.extend(isolation.unresolved_reasons)
    if config.build is None:
        blockers.append("Build or version context is not available.")
    actor = scenario.actor
    if actor is None:
        blockers.append("Actor/profile evidence is not available.")
    if config.profile is None:
        blockers.append("Actor profile context is not available.")
    permissions: list[d.Ref] = []
    if actor is not None:
        mappings = [
            node
            for node in model.nodes
            if isinstance(node, d.ActorMapping)
            and node.actor == actor
            and node.status == "confirmed"
        ]
        subjects = {actor.id} | {
            ref.id for mapping in mappings for ref in mapping.roles + mapping.groups
        }
        permissions = [
            _ref(node)
            for node in model.nodes
            if isinstance(node, d.Permission)
            and node.subject.id in subjects
            and (scenario.stimulus is None or node.action == scenario.stimulus)
        ]
    readiness: d.Readiness
    if exploratory:
        readiness = "EXPLORATORY_ONLY"
    elif blockers:
        readiness = "BLOCKED_SOURCE"
    else:
        readiness = "READY_WITH_REVIEW"
    case_id = stable_id("m3.case", model.project_id, model.snapshot_id, scenario.id)
    scenario_ref = _ref(scenario)
    step = DraftManualStep(
        number=1,
        action=action,
        path=_ref(path) if path else None,
        oracle=_ref(oracle) if oracle else None,
        expected_result=oracle.statement if oracle else None,
        evidence_expectation="Record the observation for any Fail or Blocked result.",
        blocking_reasons=blockers,
    )
    materialized: d.TestCase | None = None
    if readiness == "READY_WITH_REVIEW" and path and oracle and oracle.normative:
        materialized = d.TestCase(
            id=case_id,
            project_id=model.project_id,
            snapshot_id=model.snapshot_id,
            title=f"Review scenario {scenario.id}",
            objective=objective.text or oracle.statement,
            origin=oracle.origin,
            claims=objective.claims,
            criteria=[scenario.source_atom] if scenario.source_atom else [],
            risks=[scenario.source_risk] if scenario.source_risk else [],
            scenarios=[],
            environment=d.SupportedText(text=environment.text or "", claims=environment.claims),
            build=config.build or "",
            actor=actor,
            profile=config.profile or "",
            permissions=permissions,
            preconditions=[],
            data=[],
            steps=[
                d.ManualStep(
                    number=1,
                    action=d.SupportedText(text=action.text or "", claims=action.claims),
                    path=_ref(path),
                    oracle=_ref(oracle),
                    expected_result=oracle.statement,
                    required=True,
                    evidence_expectation="Record the observation for any Fail or Blocked result.",
                )
            ],
            pass_rule="All required steps satisfy their cited oracles.",
            fail_rule="A required observation contradicts its cited oracle.",
            blocked_rule=(
                "Required evidence, preparation, action, or observation cannot be completed."
            ),
            cleanup=d.SupportedText(text=cleanup.text or "", claims=cleanup.claims),
            isolation=d.SupportedText(text=isolation.text or "", claims=isolation.claims),
            shared_step_candidates=[],
            parameter_candidates=[],
            readiness="READY",
            blocking_notes=[],
            review_required=False,
        )
        working = model.model_copy(deep=True)
        if oracle.id not in {item.id for item in working.oracles}:
            working.oracles.append(oracle)
        if validate_test_case(materialized, working).valid:
            readiness = "READY"
        else:
            materialized = None
            blockers.append("Strict READY validation requires additional supported context.")
            readiness = "BLOCKED_SOURCE"
    proposal = GeneratedCaseProposal(
        id=case_id,
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        action="NEW",
        title=f"Review scenario {scenario.id}",
        objective=objective,
        origin=scenario.origin,
        primary_provenance=objective.claims,
        requirements=[scenario.source_requirement] if scenario.source_requirement else [],
        criteria=[scenario.source_atom] if scenario.source_atom else [],
        risks=[scenario.source_risk] if scenario.source_risk else [],
        scenarios=[scenario_ref],
        priority_rationale=scenario.rationale,
        environment=environment,
        build=config.build,
        actor=actor,
        profile=config.profile,
        permissions=permissions,
        steps=[step],
        pass_rule=None if exploratory else "All required steps satisfy their cited oracles.",
        fail_rule=None if exploratory else "A required observation contradicts its cited oracle.",
        blocked_rule="Required evidence, preparation, action, or observation cannot be completed.",
        cleanup=cleanup,
        isolation=isolation,
        evidence_expectations=["Record the failed or blocked step and relevant observation."],
        readiness=readiness,
        blocking_notes=sorted(set(blockers)),
        review_status="NOT_REQUIRED" if readiness == "READY" else "REVIEW_REQUIRED",
        rationale="Generated from an explicitly selected M2 scenario without adding behavior.",
        materialized_test=materialized,
    )
    return proposal, oracle if oracle and oracle.id not in {
        item.id for item in model.oracles
    } else None


def _brownfield_revisions(
    model: d.ProjectModel,
    analysis: M2AnalysisReport,
    cases: list[GeneratedCaseProposal],
) -> list[TestRevisionProposal]:
    tests = {node.id: node for node in model.nodes if isinstance(node, d.ExistingTest)}
    revisions: list[TestRevisionProposal] = []
    for finding in analysis.findings:
        if finding.kind != "EXISTING_TEST_AUDIT" or finding.asset is None:
            continue
        existing = tests.get(finding.asset.id)
        if existing is None:
            continue
        if finding.classification == "VALID_AS_IS":
            action: Literal["KEEP", "IMPROVE", "REVISE", "REPLACE"] = "KEEP"
        elif finding.classification == "VALID_WITH_IMPROVEMENT":
            action = "IMPROVE"
        elif finding.classification in {"STALE", "OBSOLETE_CANDIDATE", "CONFLICTING"}:
            action = "REPLACE"
        else:
            action = "REVISE"
        related = next(
            (
                case
                for case in cases
                if {ref.id for ref in case.criteria} & {ref.id for ref in existing.criterion_ids}
            ),
            None,
        )
        field_diffs = (
            []
            if action == "KEEP"
            else [
                FieldDiff(
                    field="classification",
                    kind="CHANGED",
                    before=existing.classification,
                    after=finding.classification,
                    rationale=finding.rationale,
                    evidence=finding.supporting_evidence,
                )
            ]
        )
        step_diffs = (
            [
                StepDiff(
                    kind="CHANGED",
                    rationale=(
                        "Procedure requires evidence-backed review; historical steps remain "
                        "unchanged."
                    ),
                    evidence=finding.supporting_evidence,
                )
            ]
            if action in {"REVISE", "REPLACE"}
            else []
        )
        revisions.append(
            TestRevisionProposal(
                id=stable_id(
                    "m3.revision", model.project_id, model.snapshot_id, existing.id, action
                ),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                original_test=_ref(existing),
                action=action,
                proposed_case=_ref(related) if related else None,
                field_diffs=field_diffs,
                step_diffs=step_diffs,
                rationale=finding.rationale,
                evidence=finding.supporting_evidence,
            )
        )
    return sorted(revisions, key=lambda item: item.id)


def revalidate_clone_asset(
    test: d.ExistingTest, destination: d.ProjectModel
) -> tuple[
    Literal[
        "REUSABLE", "REQUIRES_UPDATE", "OBSOLETE_CANDIDATE", "DUPLICATE", "CONFLICTING", "UNKNOWN"
    ],
    str,
]:
    """Revalidate modeled source assumptions only against destination evidence."""

    index = artifacts(destination)
    refs_to_check = (
        test.requirement_ids
        + test.criterion_ids
        + test.state_ids
        + test.channel_ids
        + test.path_ids
        + test.oracle_ids
        + test.source_assumption_refs
        + ([test.actor_id] if test.actor_id else [])
    )
    if any(ref.id not in index for ref in refs_to_check):
        return "UNKNOWN", "One or more source assumptions do not resolve in destination evidence."
    if any(
        ref.project_id != destination.project_id or ref.snapshot_id != destination.snapshot_id
        for ref in refs_to_check
    ):
        return "UNKNOWN", "Source assumptions are not bound to the destination project snapshot."
    for oracle_ref in test.oracle_ids:
        if reuse_oracle(oracle_ref, destination).status != "MATERIALIZED_NORMATIVE":
            return "CONFLICTING", "The source-project oracle is not normative in the destination."
    if not test.path_ids or test.actor_id is None or not test.oracle_ids:
        return "REQUIRES_UPDATE", "Destination path, actor, or oracle assumptions are incomplete."
    paths = [index[ref.id] for ref in test.path_ids]
    if any(
        not isinstance(path, d.VerifiedPath) or path.verification_status != "verified"
        for path in paths
    ):
        return "REQUIRES_UPDATE", "The destination operational path is not verified."
    return "REUSABLE", "All modeled assumptions resolve in current destination evidence."


def _clone_revisions(model: d.ProjectModel) -> list[TestRevisionProposal]:
    revisions: list[TestRevisionProposal] = []
    tests = sorted(
        (node for node in model.nodes if isinstance(node, d.ExistingTest)), key=lambda item: item.id
    )
    for test in tests:
        classification, rationale = revalidate_clone_asset(test, model)
        action: Literal["KEEP", "IMPROVE", "REVISE", "REPLACE"] = (
            "KEEP"
            if classification == "REUSABLE"
            else "REPLACE"
            if classification in {"OBSOLETE_CANDIDATE", "CONFLICTING"}
            else "REVISE"
        )
        revisions.append(
            TestRevisionProposal(
                id=stable_id(
                    "m3.clone", model.project_id, model.snapshot_id, test.id, classification
                ),
                project_id=model.project_id,
                snapshot_id=model.snapshot_id,
                original_test=_ref(test),
                action=action,
                field_diffs=(
                    []
                    if action == "KEEP"
                    else [
                        FieldDiff(
                            field="destination_assumptions",
                            kind="CHANGED",
                            before="source project assumptions",
                            after=classification,
                            rationale=rationale,
                            evidence=test.claims,
                        )
                    ]
                ),
                rationale=rationale,
                evidence=test.claims,
            )
        )
    return revisions


def propose_shared_steps(cases: list[GeneratedCaseProposal]) -> list[SharedStepCandidate]:
    groups: dict[tuple[str, tuple[str, ...]], list[GeneratedCaseProposal]] = {}
    for case in cases:
        for precondition in case.preconditions:
            if precondition.text and precondition.claims and not precondition.unresolved_reasons:
                key = (precondition.text, tuple(sorted(ref.id for ref in precondition.claims)))
                groups.setdefault(key, []).append(case)
    candidates: list[SharedStepCandidate] = []
    for (text, _), users in sorted(groups.items()):
        unique_users = {case.id: case for case in users}
        if len(unique_users) < 2:
            continue
        first = next(iter(unique_users.values()))
        precondition = next(item for item in first.preconditions if item.text == text)
        candidates.append(
            SharedStepCandidate(
                id=stable_id("m3.shared", first.project_id, first.snapshot_id, text),
                project_id=first.project_id,
                snapshot_id=first.snapshot_id,
                title=f"Prepare: {text}",
                steps=[DraftManualStep(number=1, action=precondition, required=True)],
                supporting_evidence=precondition.claims,
                claim_refs=precondition.claims,
                used_by=[
                    _ref(case) for case in sorted(unique_users.values(), key=lambda item: item.id)
                ],
                rationale="The same evidence-backed preparation is repeated across proposals.",
                readiness="READY_WITH_REVIEW",
                review_status="REVIEW_REQUIRED",
            )
        )
    return candidates


def propose_parameters(cases: list[GeneratedCaseProposal]) -> list[ParameterCandidate]:
    groups: dict[str, list[tuple[GeneratedCaseProposal, DraftTestData]]] = {}
    for case in cases:
        for datum in case.data:
            groups.setdefault(datum.name, []).append((case, datum))
    candidates: list[ParameterCandidate] = []
    for name, uses in sorted(groups.items()):
        first_case, first_data = uses[0]
        evidence = sorted(
            {ref.id: ref for _, data in uses for ref in data.properties.claims}.values(),
            key=lambda ref: ref.id,
        )
        if not evidence:
            continue
        candidates.append(
            ParameterCandidate(
                id=stable_id("m3.parameter", first_case.project_id, first_case.snapshot_id, name),
                project_id=first_case.project_id,
                snapshot_id=first_case.snapshot_id,
                name=name,
                properties=first_data.properties,
                source_evidence=evidence,
                used_by=[_ref(case) for case, _ in uses],
                rationale="Explicit evidence-backed test data can be supplied as a parameter.",
            )
        )
    return candidates


def generate_m3(
    model: d.ProjectModel,
    analysis: M2AnalysisReport,
    config: AuthoringConfig | None = None,
) -> M3GenerationReport:
    """Generate deterministic proposal-only M3 artifacts from exact M1/M2 inputs."""

    config = config or AuthoringConfig()
    model_result = validate_project_model(model)
    analysis_result = validate_analysis_report(analysis, model)
    if not model_result.valid or not analysis_result.valid:
        raise ValueError("Project Model and M2 analysis must validate against the same snapshot.")
    selected = {
        item.scenario.id
        for item in analysis.dispositions
        if item.disposition in {"SELECTED", "EXPLORATORY"}
    }
    scenarios = [item for item in analysis.scenarios if item.id in selected][: config.max_cases]
    cases: list[GeneratedCaseProposal] = []
    generated_oracles: list[d.Oracle] = []
    for scenario in scenarios:
        case, oracle = _case_from_scenario(scenario, model, config)
        cases.append(case)
        if oracle is not None:
            generated_oracles.append(oracle)
    cases.sort(key=lambda item: item.id)
    edges: list[GenerationTraceabilityEdge] = []
    for case in cases:
        case_ref = _ref(case)
        for relation, sources in (
            ("REQUIREMENT_TO_CASE", case.requirements),
            ("CRITERION_TO_CASE", case.criteria),
            ("RISK_TO_CASE", case.risks),
            ("SCENARIO_TO_CASE", case.scenarios),
        ):
            for source in sources:
                edges.append(
                    GenerationTraceabilityEdge(
                        id=stable_id(
                            "m3.edge",
                            model.project_id,
                            model.snapshot_id,
                            relation,
                            source.id,
                            case.id,
                        ),
                        project_id=model.project_id,
                        snapshot_id=model.snapshot_id,
                        source=source,
                        target=case_ref,
                        relation=relation,  # type: ignore[arg-type]
                        evidence=case.primary_provenance,
                    )
                )
        for claim_ref in case.primary_provenance:
            claim = next((item for item in model.claims if item.id == claim_ref.id), None)
            if claim is not None and claim.origin == "ORGANIZATIONAL_POLICY":
                edges.append(
                    GenerationTraceabilityEdge(
                        id=stable_id(
                            "m3.edge",
                            model.project_id,
                            model.snapshot_id,
                            "policy",
                            claim.id,
                            case.id,
                        ),
                        project_id=model.project_id,
                        snapshot_id=model.snapshot_id,
                        source=claim_ref,
                        target=case_ref,
                        relation="POLICY_TO_CASE",
                        evidence=[claim_ref],
                    )
                )
    config_hash = canonical_hash(config)
    binding = GenerationInputBinding(
        project_model_hash=canonical_hash(model),
        m2_analysis_hash=canonical_hash(analysis),
        generator_version=config.generator_version,
        configuration_hash=config_hash,
    )
    test_model = d.TestModel(
        id=stable_id("m3.tests", model.project_id, model.snapshot_id, binding.m2_analysis_hash),
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        test_cases=[case.materialized_test for case in cases if case.materialized_test],
        proposal_only=True,
    )
    revisions = (
        _brownfield_revisions(model, analysis, cases)
        if analysis.mode == "BROWNFIELD"
        else _clone_revisions(model)
        if analysis.mode == "CLONE_REUSE"
        else []
    )
    shared_steps = propose_shared_steps(cases)
    parameters = propose_parameters(cases)
    artifact_refs = (
        [_ref(case) for case in cases]
        + [_ref(item) for item in revisions]
        + [_ref(item) for item in shared_steps]
        + [_ref(item) for item in parameters]
    )
    manifest = GenerationManifest(
        id=stable_id("m3.manifest", model.project_id, model.snapshot_id, config_hash),
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        mode=analysis.mode,
        input_binding=binding,
        configuration={key: str(value) for key, value in config.model_dump(mode="json").items()},
        artifact_refs=artifact_refs,
        created_at=config.generated_at,
        tool_version=config.generator_version,
    )
    limitations = sorted({note for case in cases for note in case.blocking_notes})
    return M3GenerationReport(
        id=stable_id(
            "m3.report", model.project_id, model.snapshot_id, canonical_hash(analysis), config_hash
        ),
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        mode=analysis.mode,
        status="COMPLETE"
        if cases and all(not case.blocking_notes for case in cases)
        else "PARTIAL",
        input_binding=binding,
        cases=cases,
        test_model=test_model,
        revisions=revisions,
        shared_steps=shared_steps,
        parameters=parameters,
        traceability=sorted(edges, key=lambda item: item.id),
        materialized_oracles=generated_oracles,
        manifest=manifest,
        limitations=limitations or ["No selected M2 scenarios were available."],
    )


def validate_generation_report(
    report: M3GenerationReport, model: d.ProjectModel, analysis: M2AnalysisReport
) -> Result:
    result = Result()
    if report.project_id != model.project_id or report.snapshot_id != model.snapshot_id:
        result.add("M3_SCOPE", report, "M3 report and Project Model scopes differ.")
    if report.input_binding.project_model_hash != canonical_hash(model):
        result.add("M3_STALE_MODEL", report, "Project Model hash differs from the M3 binding.")
    if report.input_binding.m2_analysis_hash != canonical_hash(analysis):
        result.add("M3_STALE_ANALYSIS", report, "M2 analysis hash differs from the M3 binding.")
    if not validate_analysis_report(analysis, model).valid:
        result.add("M3_INVALID_ANALYSIS", report, "M2 analysis is invalid for the Project Model.")
    working = model.model_copy(deep=True)
    working.oracles.extend(report.materialized_oracles)
    for case in report.cases:
        if case.readiness == "READY":
            if case.materialized_test is None:
                result.add("M3_READY_DRAFT", case, "READY proposal lacks a materialized TestCase.")
            else:
                result.issues.extend(validate_test_case(case.materialized_test, working).issues)
        if case.origin in {"RISK", "EXPLORATORY"} and case.readiness != "EXPLORATORY_ONLY":
            result.add("M3_RISK_LEAKAGE", case, "Risk/exploratory proposal became normative.")
    return result
