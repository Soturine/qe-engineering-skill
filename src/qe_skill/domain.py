"""Versioned data contracts. Parsing never executes evidence or resolves remote links."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Text = Annotated[str, Field(min_length=1, pattern=r"\S")]
Digest = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
Timestamp = Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")]
Origin = Literal["CONTRACT", "IMPLEMENTATION", "ORGANIZATIONAL_POLICY", "RISK", "EXPLORATORY"]
Completeness = Literal["COMPLETE", "SCOPED_COMPLETE", "PARTIAL", "INVALID"]
Readiness = Literal[
    "READY",
    "READY_WITH_REVIEW",
    "AMBIGUOUS",
    "BLOCKED_SOURCE",
    "EXPLORATORY_ONLY",
    "REJECTED_DUPLICATE",
    "REJECTED_UNSUPPORTED_ORACLE",
]


class Record(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, validate_assignment=True)


class Artifact(Record):
    schema_version: Literal["1.0"] = "1.0"
    id: Text
    project_id: Text
    snapshot_id: Text


class Ref(Record):
    id: Text
    project_id: Text
    snapshot_id: Text


class Extraction(Record):
    method: Text
    version: Text
    provider: Text | None = None
    model: Text | None = None
    prompt_version: Text | None = None


class Source(Artifact):
    source_type: Text
    locator: Text
    version: Text | None = None
    content_hash: Digest | None = None
    hash_unavailable_reason: Text | None = None
    collected_at: Timestamp
    authority_class: Literal[
        "CONTRACT",
        "TECHNICAL_CONTRACT",
        "ORGANIZATIONAL_POLICY",
        "IMPLEMENTATION",
        "HISTORICAL",
        "GUIDANCE",
    ]
    lifecycle: Literal[
        "draft",
        "approved",
        "active",
        "superseded",
        "deprecated",
        "archived",
        "unknown",
    ]
    study_status: Literal[
        "STUDIED",
        "PARTIALLY_STUDIED",
        "NOT_STUDIED",
        "BLOCKED",
        "OUT_OF_SCOPE",
        "SUPERSEDED",
    ]
    read_integrity: Literal[
        "COMPLETE",
        "PARTIAL",
        "TRUNCATED",
        "FAILED",
        "UNVERIFIED",
        "NOT_APPLICABLE",
    ]
    required: bool
    in_scope: bool
    reason: Text | None = None
    primary: bool
    extraction: Extraction
    sensitivity: Text
    handling: Text


class ScopeEntry(Record):
    source: Ref
    required: bool
    in_scope: bool
    decision_reason: Text | None = None


class RunManifest(Artifact):
    mode: Literal["GREENFIELD", "BROWNFIELD", "CLONE_REUSE", "REGRESSION_AUDIT"]
    scope_description: Text
    scope: list[ScopeEntry]
    containers: list[Text]
    inventory_complete: bool
    completeness: Completeness
    created_at: Timestamp
    tool_version: Text
    authority_policy: Text


class SourceLedger(Artifact):
    manifest: RunManifest
    sources: list[Source]


class Evidence(Record):
    source: Ref
    source_hash: Digest
    location: Text


class Claim(Artifact):
    statement: Text
    origin: Origin
    evidence: list[Evidence]
    inferred: bool
    confidence: Annotated[float, Field(ge=0, le=1)]
    extraction: Extraction
    derived_from: list[Ref] = Field(default_factory=list)
    conflict: Literal["none", "unresolved", "resolved"]


class Oracle(Artifact):
    statement: Text
    origin: Origin
    claim: Ref
    normative: bool
    inferred: bool
    confidence: Annotated[float, Field(ge=0, le=1)]
    usage: Literal["acceptance", "characterization", "exploration"]
    approval_id: Text | None = None
    invariant_claim: Ref | None = None


class Operation(Record):
    id: Text
    kind: Literal["create", "update", "link", "append", "promote_oracle"]
    target: Text
    target_version: Text
    artifact: Ref
    artifact_hash: Digest
    payload_hash: Digest
    preserve_history: Literal[True]
    idempotency_key: Text


class Proposal(Artifact):
    operations: list[Operation] = Field(min_length=1)
    preview_hash: Digest
    source_snapshot: Text
    target_snapshot: Text
    evidence_hash: Digest | None = None


class Approval(Artifact):
    actor: Text
    authority: Text
    timestamp: Timestamp
    decision: Literal["APPROVED", "REJECTED"]
    reason: Text
    proposal_id: Text
    proposal_hash: Digest
    source_snapshot: Text
    target_snapshot: Text
    operation_ids: list[Text] = Field(min_length=1)


class Node(Artifact):
    name: Text
    claims: list[Ref]


class Constraint(Node):
    kind: Literal["constraint"] = "constraint"
    statement: Text


class Entity(Node):
    kind: Literal["entity"] = "entity"
    category: Literal["business", "technical", "physical", "external", "unknown"]
    fields: list[Ref] = Field(default_factory=list)
    relationships: list[Ref] = Field(default_factory=list)
    constraints: list[Ref] = Field(default_factory=list)
    states: list[Ref] = Field(default_factory=list)


class ModelField(Node):
    kind: Literal["field"] = "field"
    entity: Ref
    data_type: Text
    required: bool | Literal["unknown"]
    constraints: list[Ref] = Field(default_factory=list)
    aliases: list[Text] = Field(default_factory=list)


class Relationship(Node):
    kind: Literal["relationship"] = "relationship"
    from_entity: Ref
    to_entity: Ref
    relationship_type: Literal[
        "one_to_one",
        "one_to_many",
        "many_to_many",
        "owns",
        "references",
        "contains",
        "derived",
        "unknown",
    ]
    cardinality: Text | None = None
    constraints: list[Ref] = Field(default_factory=list)


class Actor(Node):
    kind: Literal["actor"] = "actor"


class Role(Node):
    kind: Literal["role"] = "role"


class Group(Node):
    kind: Literal["group"] = "group"


class ActorMapping(Node):
    kind: Literal["actor_mapping"] = "actor_mapping"
    actor: Ref
    roles: list[Ref]
    groups: list[Ref]
    status: Literal["confirmed", "proposed", "conflicting", "unresolved"]


class Permission(Node):
    kind: Literal["permission"] = "permission"
    subject: Ref
    resource: Ref
    action: Ref
    scope: Text
    effect: Literal["allow", "deny", "conditional"]
    conditions: list[Ref] = Field(default_factory=list)


class State(Node):
    kind: Literal["state"] = "state"
    entity: Ref
    terminal: bool | Literal["unknown"]


class Transition(Node):
    kind: Literal["transition"] = "transition"
    entity: Ref
    from_state: Ref | None
    to_state: Ref | None
    trigger: Ref
    actors: list[Ref] = Field(default_factory=list)
    roles: list[Ref] = Field(default_factory=list)
    channels: list[Ref] = Field(default_factory=list)
    preconditions: list[Ref] = Field(default_factory=list)
    guards: list[Ref] = Field(default_factory=list)
    postconditions: list[Ref] = Field(default_factory=list)
    side_effects: list[Ref] = Field(default_factory=list)
    exceptions: list[Ref] = Field(default_factory=list)
    classification: Literal["normal", "exception", "contingency", "invalid", "recovery", "unknown"]


class Channel(Node):
    kind: Literal["channel"] = "channel"
    channel_type: Literal[
        "ui",
        "api",
        "cli",
        "event",
        "queue",
        "batch",
        "device",
        "file",
        "physical",
        "external",
        "other",
    ]
    interfaces: list[Ref]


class Action(Node):
    kind: Literal["action"] = "action"
    actors: list[Ref] = Field(default_factory=list)
    input_constraints: list[Ref] = Field(default_factory=list)
    output_claims: list[Ref] = Field(default_factory=list)
    side_effects: list[Ref] = Field(default_factory=list)


class Event(Node):
    kind: Literal["event"] = "event"
    producer: Text
    consumer: Text
    delivery_claim: Ref | None = None
    ordering_claim: Ref | None = None


class Interface(Node):
    kind: Literal["interface"] = "interface"
    interface_type: Literal[
        "http_api",
        "rpc",
        "event",
        "queue",
        "file",
        "database",
        "device",
        "ui",
        "cli",
        "other",
    ]
    producer: Text
    consumer: Text
    contract_sources: list[Ref]
    authentication: Ref | None = None
    authorization: Ref | None = None
    timeout: Ref | None = None
    retry: Ref | None = None
    idempotency: Ref | None = None
    ordering: Ref | None = None
    failure_behavior: Ref | None = None
    implementation_symbols: list[Text] = Field(default_factory=list)


class Integration(Node):
    kind: Literal["integration"] = "integration"
    interfaces: list[Ref]
    producer: Text
    consumer: Text


class Requirement(Node):
    kind: Literal["requirement"] = "requirement"
    lifecycle: Literal["draft", "approved", "active", "superseded", "deprecated", "unknown"]


class AtomicCriterion(Node):
    kind: Literal["atomic_criterion"] = "atomic_criterion"
    requirement: Ref
    statement: Text
    states: list[Ref] = Field(default_factory=list)
    actors: list[Ref] = Field(default_factory=list)
    channels: list[Ref] = Field(default_factory=list)
    boundaries: list[Ref] = Field(default_factory=list)
    timing: list[Ref] = Field(default_factory=list)
    failure_modes: list[Ref] = Field(default_factory=list)


class Invariant(Node):
    kind: Literal["invariant"] = "invariant"
    statement: Text
    origin: Origin
    scope: Text


class Ambiguity(Node):
    kind: Literal["ambiguity"] = "ambiguity"
    question: Text
    affected: list[Ref]
    risk_of_guessing: Text
    status: Literal["open", "resolved"]
    resolution_claim: Ref | None = None


class Conflict(Node):
    kind: Literal["conflict"] = "conflict"
    conflicting_claims: list[Ref] = Field(min_length=2)
    affected: list[Ref]
    status: Literal["unresolved", "resolved"]
    resolution_claim: Ref | None = None


class Alias(Node):
    kind: Literal["alias"] = "alias"
    canonical: Ref
    alias: Text
    confidence: Annotated[float, Field(ge=0, le=1)]
    status: Literal["confirmed", "proposed", "conflicting"]


class Risk(Node):
    kind: Literal["risk"] = "risk"
    category: Text
    description: Text
    affected: list[Ref]
    severity: Text
    scale: Text
    derivation: Text


class Scenario(Node):
    kind: Literal["scenario"] = "scenario"
    origin: Origin
    preconditions: list[Ref]
    stimulus: Ref
    oracle: Ref | None
    risks: list[Ref]
    selected_for_test: bool
    selection_reason: Text


class HistoricalIdentity(Record):
    """Opaque historical metadata, never a resolvable destination evidence reference."""

    external_id: Text
    source_project: Text
    source_snapshot: Text
    version: Text
    history_locators: list[Text]
    content_hash: Digest


class ExistingTest(Node):
    kind: Literal["existing_test"] = "existing_test"
    historical: HistoricalIdentity
    original_text: Text
    classification: Literal[
        "UNKNOWN",
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
        "REQUIRES_UPDATE",
        "REUSABLE",
    ]


class ExistingResult(Node):
    kind: Literal["existing_result"] = "existing_result"
    historical: HistoricalIdentity
    test: Ref | None = None
    outcome: Literal["PASS", "FAIL", "BLOCKED", "NOT_RUN", "UNKNOWN"]
    observed_at: Timestamp | None = None
    original_text: Text


class GeneratedTest(Node):
    kind: Literal["generated_test"] = "generated_test"
    test_case: Ref
    replaces: Ref | None = None


class PathStep(Record):
    instruction: Text
    claim: Ref


class VerifiedPath(Node):
    kind: Literal["verified_path"] = "verified_path"
    path_type: Literal["ui", "api", "cli", "physical", "mixed"]
    steps: list[PathStep] = Field(min_length=1)
    verification_status: Literal["verified", "partial", "unresolved"]


SemanticNode = Annotated[
    Entity
    | ModelField
    | Constraint
    | Relationship
    | Actor
    | Role
    | Group
    | ActorMapping
    | Permission
    | State
    | Transition
    | Channel
    | Action
    | Event
    | Interface
    | Integration
    | Requirement
    | AtomicCriterion
    | Invariant
    | Ambiguity
    | Conflict
    | Alias
    | Risk
    | Scenario
    | ExistingTest
    | ExistingResult
    | GeneratedTest
    | VerifiedPath,
    Field(discriminator="kind"),
]


class SupportedText(Record):
    text: Text
    claims: list[Ref]


class TestData(Record):
    name: Text
    properties: SupportedText
    preparation: SupportedText
    parameter: bool


class ManualStep(Record):
    number: Annotated[int, Field(ge=1)]
    action: SupportedText
    path: Ref
    oracle: Ref | None
    expected_result: Text | None
    required: bool
    evidence_expectation: Text


class TestCase(Artifact):
    title: Text
    objective: Text
    origin: Origin
    claims: list[Ref]
    criteria: list[Ref]
    risks: list[Ref]
    scenarios: list[Ref]
    environment: SupportedText
    build: Text
    actor: Ref | None
    profile: Text
    permissions: list[Ref]
    preconditions: list[SupportedText]
    data: list[TestData]
    steps: list[ManualStep]
    pass_rule: Text | None
    fail_rule: Text | None
    blocked_rule: Text
    cleanup: SupportedText
    isolation: SupportedText
    shared_step_candidates: list[Ref]
    parameter_candidates: list[Text]
    readiness: Readiness
    blocking_notes: list[Text]
    review_required: bool
    review_approval_id: Text | None = None


class TestModel(Artifact):
    test_cases: list[TestCase]
    proposal_only: Literal[True]


class ProjectModel(Artifact):
    ledger: SourceLedger
    claims: list[Claim]
    oracles: list[Oracle]
    nodes: list[SemanticNode]
    tests: TestModel
    proposals: list[Proposal] = Field(default_factory=list)
    approvals: list[Approval] = Field(default_factory=list)
