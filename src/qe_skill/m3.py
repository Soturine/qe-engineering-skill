"""Typed M3 authoring contracts.

The contracts deliberately separate unresolved authoring proposals from strict
``TestCase`` artifacts. Generation and trust validation are implemented in later
M3 stages; these records perform shape, readiness, and scope checks only.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from qe_skill import domain as d

GenerationMode = Literal["GREENFIELD", "BROWNFIELD", "CLONE_REUSE"]
ProposalAction = Literal["NEW", "KEEP", "IMPROVE", "REVISE", "REPLACE"]
ReviewStatus = Literal["NOT_REQUIRED", "REVIEW_REQUIRED", "APPROVED", "REJECTED"]
DiffKind = Literal["ADDED", "REMOVED", "CHANGED", "UNCHANGED"]


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
