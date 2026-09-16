"""Small evidence-bound semantic relation graph and non-authoritative adjudication for M4.H4."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from typing import Literal, cast

from pydantic import Field

from qe_skill import domain as d
from qe_skill.normalization import (
    NormalizedSemanticRecord,
    SemanticNormalizationSet,
    validate_normalization_set,
)
from qe_skill.reasoning import ReasoningRequest, ReasoningResult, canonical_hash
from qe_skill.semantic import SemanticCandidate, SemanticCandidateSet, validate_candidate_set
from qe_skill.validation import Result, same_scope

RelationKind = Literal[
    "CONSISTENT",
    "CONFLICTING",
    "REFINEMENT",
    "SUPERSEDED",
    "DEPLOYMENT_INSTANCE",
    "AMBIGUOUS",
    "HUMAN_DECISION_REQUIRED",
]
RELATION_KINDS = {
    "CONSISTENT",
    "CONFLICTING",
    "REFINEMENT",
    "SUPERSEDED",
    "DEPLOYMENT_INSTANCE",
    "AMBIGUOUS",
    "HUMAN_DECISION_REQUIRED",
}
AdjudicationOutcome = Literal[
    "PRESERVE_BOTH",
    "PRESERVE_CONFLICT",
    "RECORD_REFINEMENT",
    "RECORD_SUPERSESSION",
    "RECORD_DEPLOYMENT_INSTANCE",
    "HUMAN_REVIEW_REQUIRED",
]


class NormalizationBinding(d.Record):
    normalization_set: d.Ref
    normalization_set_hash: d.Digest


class RelationInput(d.Record):
    """Evidence envelope; callers supply the current ledger, never provider-owned authority."""

    normalization: SemanticNormalizationSet
    candidates: SemanticCandidateSet
    request: ReasoningRequest
    result: ReasoningResult
    ledger: d.SourceLedger


class RelationCandidateInput(d.Record):
    """Validated H2 envelope for optional provider-proposed pair relationships."""

    candidates: SemanticCandidateSet
    request: ReasoningRequest
    result: ReasoningResult
    ledger: d.SourceLedger


class CandidateSetBinding(d.Record):
    candidate_set: d.Ref
    candidate_set_hash: d.Digest


class RelationAuthorityContext(d.Record):
    left_authority: list[d.Text]
    right_authority: list[d.Text]
    left_lifecycle: list[d.Text]
    right_lifecycle: list[d.Text]


class SemanticRelation(d.Artifact):
    left: d.Ref
    left_hash: d.Digest
    right: d.Ref
    right_hash: d.Digest
    relation: RelationKind
    rationale_codes: list[d.Text] = Field(min_length=1)
    authority_context: RelationAuthorityContext
    provider_candidate_relation: RelationKind | None = None
    provider_candidate: d.Ref | None = None
    provider_candidate_hash: d.Digest | None = None
    refinement_record: d.Ref | None = None
    superseded_record: d.Ref | None = None
    deployment_record: d.Ref | None = None
    confidence_used_to_select_winner: Literal[False] = False
    authority_changed: Literal[False] = False


class AdjudicationResult(d.Artifact):
    relation: d.Ref
    relation_hash: d.Digest
    outcome: AdjudicationOutcome
    human_review_required: bool
    winner: None = None
    conflict_preserved: bool
    facts_promoted: Literal[False] = False
    provider_self_authorized: Literal[False] = False


class SemanticRelationGraph(d.Artifact):
    inputs: list[NormalizationBinding] = Field(min_length=1)
    candidate_inputs: list[CandidateSetBinding] = Field(default_factory=list)
    max_records: int = Field(ge=2, le=1_000)
    status: Literal["COMPLETE", "EMPTY", "REJECTED"]
    relations: list[SemanticRelation]
    adjudications: list[AdjudicationResult]
    limitations: list[d.Text] = Field(default_factory=list)
    external_writes: Literal[False] = False
    authority_changed: Literal[False] = False
    facts_promoted: Literal[False] = False


def _ref(record: d.Artifact) -> d.Ref:
    return d.Ref(id=record.id, project_id=record.project_id, snapshot_id=record.snapshot_id)


def _pair(left: str, right: str) -> tuple[str, str]:
    return (left, right) if left <= right else (right, left)


def _authorities(record: NormalizedSemanticRecord) -> tuple[list[str], list[str]]:
    return (
        sorted({item.authority_class for item in record.original_statements}),
        sorted({item.source_lifecycle for item in record.original_statements}),
    )


def _concept(record: NormalizedSemanticRecord, name: str) -> str | None:
    value = getattr(record.meaning, name)
    return value.label.casefold() if value else None


def _subject(record: NormalizedSemanticRecord) -> tuple[str | None, str | None, str | None]:
    return (_concept(record, "actor"), _concept(record, "capability"), _concept(record, "intent"))


def _constraint_keys(record: NormalizedSemanticRecord) -> set[str]:
    return {
        json.dumps(
            {
                "kind": item.kind.casefold(),
                "operator": item.operator,
                "value": item.value,
                "unit": item.unit.casefold() if item.unit else None,
            },
            sort_keys=True,
            ensure_ascii=False,
        )
        for item in record.meaning.constraints
    }


def _term_keys(record: NormalizedSemanticRecord) -> set[tuple[str, str]]:
    return {(item.role, item.label.casefold()) for item in record.meaning.terms}


def _same_evidence(left: NormalizedSemanticRecord, right: NormalizedSemanticRecord) -> bool:
    def keys(record: NormalizedSemanticRecord) -> set[tuple[str, str, str, str]]:
        return {
            (item.source.id, item.source_hash, item.location, item.text)
            for item in record.original_statements
        }

    return bool(keys(left) & keys(right))


def _is_superseded(record: NormalizedSemanticRecord) -> bool:
    return bool(record.original_statements) and all(
        item.source_lifecycle in {"superseded", "deprecated", "archived"}
        for item in record.original_statements
    )


def _incompatible(left: NormalizedSemanticRecord, right: NormalizedSemanticRecord) -> bool:
    left_meaning, right_meaning = left.meaning, right.meaning
    modality_conflict = (
        left_meaning.modality != "UNSPECIFIED"
        and right_meaning.modality != "UNSPECIFIED"
        and left_meaning.modality != right_meaning.modality
    )
    polarity_conflict = (
        left_meaning.polarity != "UNSPECIFIED"
        and right_meaning.polarity != "UNSPECIFIED"
        and left_meaning.polarity != right_meaning.polarity
    )
    left_constraints: dict[tuple[str, str, str | None], set[str]] = {}
    right_constraints: dict[tuple[str, str, str | None], set[str]] = {}
    for item in left_meaning.constraints:
        left_constraints.setdefault((item.kind.casefold(), item.operator, item.unit), set()).add(
            json.dumps(item.value, sort_keys=True)
        )
    for item in right_meaning.constraints:
        right_constraints.setdefault((item.kind.casefold(), item.operator, item.unit), set()).add(
            json.dumps(item.value, sort_keys=True)
        )
    constraint_conflict = any(
        key in right_constraints and value != right_constraints[key]
        for key, value in left_constraints.items()
    )
    left_terms: dict[str, set[str]] = {}
    right_terms: dict[str, set[str]] = {}
    for term in left_meaning.terms:
        left_terms.setdefault(term.role, set()).add(term.label.casefold())
    for term in right_meaning.terms:
        right_terms.setdefault(term.role, set()).add(term.label.casefold())
    term_conflict = any(
        role in right_terms and label != right_terms[role] for role, label in left_terms.items()
    )
    return modality_conflict or polarity_conflict or constraint_conflict or term_conflict


def classify_relation(
    left: NormalizedSemanticRecord, right: NormalizedSemanticRecord
) -> tuple[RelationKind, list[str], NormalizedSemanticRecord | None]:
    """Classify a pair without using confidence or choosing a normative winner."""

    same_subject = _subject(left) == _subject(right) and any(_subject(left))
    if _same_evidence(left, right) and left.comparison_key != right.comparison_key:
        return "HUMAN_DECISION_REQUIRED", ["PROVIDER_OR_INTERPRETATION_DISAGREEMENT"], None
    if not same_subject:
        return "AMBIGUOUS", ["SUBJECT_ALIGNMENT_UNPROVEN"], None
    if _is_superseded(left) or _is_superseded(right):
        return "HUMAN_DECISION_REQUIRED", ["EXPLICIT_REPLACEMENT_LINK_REQUIRED"], None
    if left.comparison_key == right.comparison_key:
        return "CONSISTENT", ["NORMALIZED_MEANING_MATCH"], None
    left_details = _constraint_keys(left) | {
        f"term:{role}:{label}" for role, label in _term_keys(left)
    }
    right_details = _constraint_keys(right) | {
        f"term:{role}:{label}" for role, label in _term_keys(right)
    }
    same_core = (
        left.meaning.record_kind == right.meaning.record_kind
        and left.meaning.modality == right.meaning.modality
        and left.meaning.polarity == right.meaning.polarity
    )
    if same_core and left_details > right_details:
        return "REFINEMENT", ["LEFT_ADDS_GROUNDED_DETAIL"], left
    if same_core and right_details > left_details:
        return "REFINEMENT", ["RIGHT_ADDS_GROUNDED_DETAIL"], right
    if _incompatible(left, right):
        return "CONFLICTING", ["INCOMPATIBLE_NORMALIZED_MEANING"], None
    return "AMBIGUOUS", ["RELATION_NOT_DETERMINISTICALLY_PROVEN"], None


def _relation(
    left: NormalizedSemanticRecord,
    right: NormalizedSemanticRecord,
    provider_candidate: tuple[SemanticCandidate, RelationKind] | None = None,
) -> SemanticRelation:
    relation, reasons, directional = classify_relation(left, right)
    if provider_candidate:
        _, candidate_relation = provider_candidate
        if relation in {"AMBIGUOUS", "HUMAN_DECISION_REQUIRED"}:
            relation = "HUMAN_DECISION_REQUIRED"
            reasons.append("PROVIDER_RELATION_CANDIDATE_REQUIRES_REVIEW")
        elif candidate_relation != relation:
            reasons.append("PROVIDER_CANDIDATE_DIFFERS_FROM_DETERMINISTIC")
    left_authority, left_lifecycle = _authorities(left)
    right_authority, right_lifecycle = _authorities(right)
    left_hash, right_hash = canonical_hash(left), canonical_hash(right)
    seed = json.dumps(
        [
            left_hash,
            right_hash,
            relation,
            reasons,
            canonical_hash(provider_candidate[0]) if provider_candidate else None,
            provider_candidate[1] if provider_candidate else None,
        ],
        separators=(",", ":"),
    )
    return SemanticRelation(
        id=f"semantic-relation.{hashlib.sha256(seed.encode()).hexdigest()[:24]}",
        project_id=left.project_id,
        snapshot_id=left.snapshot_id,
        left=_ref(left),
        left_hash=left_hash,
        right=_ref(right),
        right_hash=right_hash,
        relation=relation,
        rationale_codes=reasons,
        authority_context=RelationAuthorityContext(
            left_authority=left_authority,
            right_authority=right_authority,
            left_lifecycle=left_lifecycle,
            right_lifecycle=right_lifecycle,
        ),
        provider_candidate_relation=provider_candidate[1] if provider_candidate else None,
        provider_candidate=_ref(provider_candidate[0]) if provider_candidate else None,
        provider_candidate_hash=canonical_hash(provider_candidate[0])
        if provider_candidate
        else None,
        refinement_record=_ref(directional) if relation == "REFINEMENT" and directional else None,
        superseded_record=_ref(directional) if relation == "SUPERSEDED" and directional else None,
        deployment_record=(
            _ref(directional) if relation == "DEPLOYMENT_INSTANCE" and directional else None
        ),
    )


def _adjudication(relation: SemanticRelation) -> AdjudicationResult:
    outcomes: dict[RelationKind, AdjudicationOutcome] = {
        "CONSISTENT": "PRESERVE_BOTH",
        "CONFLICTING": "PRESERVE_CONFLICT",
        "REFINEMENT": "RECORD_REFINEMENT",
        "SUPERSEDED": "RECORD_SUPERSESSION",
        "DEPLOYMENT_INSTANCE": "RECORD_DEPLOYMENT_INSTANCE",
        "AMBIGUOUS": "HUMAN_REVIEW_REQUIRED",
        "HUMAN_DECISION_REQUIRED": "HUMAN_REVIEW_REQUIRED",
    }
    relation_hash = canonical_hash(relation)
    identifier = hashlib.sha256((relation_hash + outcomes[relation.relation]).encode()).hexdigest()
    return AdjudicationResult(
        id=f"semantic-adjudication.{identifier[:24]}",
        project_id=relation.project_id,
        snapshot_id=relation.snapshot_id,
        relation=_ref(relation),
        relation_hash=relation_hash,
        outcome=outcomes[relation.relation],
        human_review_required=(
            relation.relation in {"CONFLICTING", "AMBIGUOUS", "HUMAN_DECISION_REQUIRED"}
            or "PROVIDER_CANDIDATE_DIFFERS_FROM_DETERMINISTIC" in relation.rationale_codes
        ),
        conflict_preserved=relation.relation == "CONFLICTING",
    )


def build_relation_graph(
    inputs: list[RelationInput],
    *,
    relation_candidates: list[RelationCandidateInput] | None = None,
    max_records: int = 100,
) -> SemanticRelationGraph:
    relation_candidates = relation_candidates or []
    normalization_sets = [item.normalization for item in inputs]
    if not normalization_sets:
        raise ValueError("relation graph requires at least one normalization set")
    root = normalization_sets[0]
    bindings = [
        NormalizationBinding(
            normalization_set=_ref(item), normalization_set_hash=canonical_hash(item)
        )
        for item in normalization_sets
    ]
    candidate_bindings = [
        CandidateSetBinding(
            candidate_set=_ref(item.candidates),
            candidate_set_hash=canonical_hash(item.candidates),
        )
        for item in relation_candidates
    ]
    identity = json.dumps(
        [
            [item.normalization_set_hash for item in bindings],
            [item.candidate_set_hash for item in candidate_bindings],
            max_records,
        ],
        separators=(",", ":"),
    )
    identifier = hashlib.sha256(identity.encode()).hexdigest()[:24]

    def graph(
        status: Literal["COMPLETE", "EMPTY", "REJECTED"],
        relations: list[SemanticRelation] | None = None,
        adjudications: list[AdjudicationResult] | None = None,
        limitations: list[str] | None = None,
    ) -> SemanticRelationGraph:
        return SemanticRelationGraph(
            id=f"semantic-relations.{identifier}",
            project_id=root.project_id,
            snapshot_id=root.snapshot_id,
            inputs=bindings,
            candidate_inputs=candidate_bindings,
            max_records=max_records,
            status=status,
            relations=relations or [],
            adjudications=adjudications or [],
            limitations=limitations or [],
        )

    if not all(same_scope(root, item) for item in normalization_sets):
        return graph(
            "REJECTED", limitations=["Normalization sets cross project or snapshot scope."]
        )
    for item in inputs:
        if (
            item.normalization.status != "COMPLETE"
            or not validate_normalization_set(
                item.normalization, item.candidates, item.request, item.result, item.ledger
            ).valid
        ):
            return graph(
                "REJECTED", limitations=["Normalization evidence is invalid or incomplete."]
            )
    records = [record for item in normalization_sets for record in item.records]
    record_ids = {record.id for record in records}
    records_by_id = {record.id: record for record in records}
    provider_relations: dict[tuple[str, str], tuple[SemanticCandidate, RelationKind]] = {}
    for envelope in relation_candidates:
        if (
            envelope.request.operation != "RELATE"
            or envelope.candidates.status != "READY_FOR_REVIEW"
            or not validate_candidate_set(
                envelope.candidates, envelope.request, envelope.result, envelope.ledger
            ).valid
            or not same_scope(root, envelope.candidates)
        ):
            return graph(
                "REJECTED", limitations=["Provider relation evidence is invalid or incomplete."]
            )
        for candidate in envelope.candidates.candidates:
            value = candidate.structured_value.get("semantic_relation")
            if candidate.candidate_type != "semantic_relation_candidate" or not isinstance(
                value, dict
            ):
                return graph(
                    "REJECTED", limitations=["Provider relation candidate shape is invalid."]
                )
            left_id = value.get("left_record_id")
            right_id = value.get("right_record_id")
            proposed = value.get("relation")
            if (
                not isinstance(left_id, str)
                or not isinstance(right_id, str)
                or left_id == right_id
                or bool({left_id, right_id} - record_ids)
                or proposed not in RELATION_KINDS
            ):
                return graph(
                    "REJECTED", limitations=["Provider relation candidate target is invalid."]
                )
            cited_sources = {item.source.id for item in candidate.evidence}
            supported_ids = {item.id for item in envelope.request.supported_facts}
            required_sources = {
                statement.source.id
                for record_id in (left_id, right_id)
                for statement in records_by_id[record_id].original_statements
            }
            if not required_sources <= cited_sources or not {left_id, right_id} <= supported_ids:
                return graph(
                    "REJECTED",
                    limitations=["Provider relation candidate does not cite both record sources."],
                )
            pair = _pair(left_id, right_id)
            if pair in provider_relations:
                return graph(
                    "REJECTED", limitations=["Provider relation candidates are not unique."]
                )
            provider_relations[pair] = (candidate, cast(RelationKind, proposed))
    if not all(same_scope(root, record) for record in records):
        return graph(
            "REJECTED", limitations=["Normalized records cross project or snapshot scope."]
        )
    if len({record.id for record in records}) != len(records):
        return graph("REJECTED", limitations=["Normalized record identifiers are not unique."])
    if len(records) > max_records:
        return graph("REJECTED", limitations=["Relation analysis exceeds the configured bound."])
    if len(records) < 2:
        return graph("EMPTY", limitations=["At least two normalized records are required."])
    relations = [
        _relation(left, right, provider_relations.get(_pair(left.id, right.id)))
        for left, right in combinations(records, 2)
    ]
    return graph("COMPLETE", relations, [_adjudication(item) for item in relations])


def validate_relation_graph(
    artifact: SemanticRelationGraph,
    inputs: list[RelationInput],
    relation_candidates: list[RelationCandidateInput] | None = None,
) -> Result:
    result = Result()
    if not inputs or not same_scope(artifact, inputs[0].normalization):
        result.add("REL_SCOPE", artifact, "Relation graph crosses project or snapshot scope.")
        return result
    expected = build_relation_graph(
        inputs, relation_candidates=relation_candidates, max_records=artifact.max_records
    )
    if artifact != expected:
        result.add(
            "REL_BINDING",
            artifact,
            "Relation graph, authority context or adjudication does not match reconstruction.",
        )
    return result
