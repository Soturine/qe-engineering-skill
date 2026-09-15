"""Provenance-bound semantic candidates and exact cache identity.

Candidates are review material, never Project Model facts or normative oracles.
"""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import Field, JsonValue, model_validator

from qe_skill import domain as d
from qe_skill.reasoning import (
    ProviderIdentity,
    ReasoningOperation,
    ReasoningRequest,
    ReasoningResult,
    canonical_hash,
)
from qe_skill.validation import Result, same_scope, validate_ledger

InterpretationClass = Literal["explicit", "structural", "heuristic", "inferred", "unresolved"]
CandidateProducer = Literal["DETERMINISTIC", "HEURISTIC", "PROVIDER"]
CandidateReviewState = Literal["PENDING_REVIEW", "REVIEW_REQUIRED", "BLOCKED_SOURCE"]
CandidateSetStatus = Literal[
    "NOT_REQUESTED", "READY_FOR_REVIEW", "PARTIAL", "BLOCKED_PROVIDER", "STALE_INPUT", "REJECTED"
]


class CandidateEvidence(d.Record):
    excerpt: d.Ref
    source: d.Ref
    source_hash: d.Digest
    location: d.Text
    span: d.Ref | None = None
    authority_class: Literal[
        "CONTRACT",
        "TECHNICAL_CONTRACT",
        "ORGANIZATIONAL_POLICY",
        "IMPLEMENTATION",
        "HISTORICAL",
        "GUIDANCE",
    ]
    source_lifecycle: Literal[
        "draft", "approved", "active", "superseded", "deprecated", "archived", "unknown"
    ]


class SemanticCandidate(d.Artifact):
    candidate_type: d.Text
    statement: d.Text | None = None
    structured_value: dict[str, JsonValue] = Field(default_factory=dict)
    evidence: list[CandidateEvidence] = Field(min_length=1)
    interpretation: InterpretationClass
    confidence: float = Field(ge=0, le=1)
    inferred: bool
    producer: CandidateProducer
    provider_identity: ProviderIdentity | None = None
    operation: ReasoningOperation
    prompt_version: d.Text
    configuration_hash: d.Digest
    extractor_version: d.Text
    run_id: d.Text
    created_at: d.Timestamp
    review_state: CandidateReviewState
    normative: Literal[False] = False
    authority_promoted: Literal[False] = False

    @model_validator(mode="after")
    def validate_candidate(self) -> SemanticCandidate:
        if self.statement is None and not self.structured_value:
            raise ValueError("semantic candidate requires statement or structured value")
        if self.producer == "PROVIDER":
            if self.provider_identity is None or not self.inferred:
                raise ValueError("provider candidates require identity and inferred state")
            if self.interpretation not in {"inferred", "unresolved"}:
                raise ValueError("provider candidates cannot claim explicit interpretation")
        elif self.provider_identity is not None:
            raise ValueError("non-provider candidate cannot claim provider identity")
        for item in self.evidence:
            for ref in (item.excerpt, item.source, item.span):
                if ref is not None and (
                    ref.project_id != self.project_id or ref.snapshot_id != self.snapshot_id
                ):
                    raise ValueError("cross-scope semantic candidate evidence")
        return self


class CacheSourceBinding(d.Record):
    source: d.Ref
    source_hash: d.Digest


class SemanticCacheBinding(d.Record):
    project_id: d.Text
    snapshot_id: d.Text
    sources: list[CacheSourceBinding] = Field(min_length=1)
    provider_identity: ProviderIdentity | None
    operation: ReasoningOperation
    prompt_version: d.Text
    configuration_hash: d.Digest
    extractor_version: d.Text


class SemanticCandidateSet(d.Artifact):
    request: d.Ref
    request_hash: d.Digest
    result: d.Ref
    result_hash: d.Digest
    cache_binding: SemanticCacheBinding
    cache_key: d.Digest
    status: CandidateSetStatus
    candidates: list[SemanticCandidate]
    limitations: list[d.Text] = Field(default_factory=list)
    external_writes: Literal[False] = False
    authority_changed: Literal[False] = False


def semantic_cache_key(binding: SemanticCacheBinding) -> str:
    payload = json.dumps(
        binding.model_dump(mode="json"), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _binding(
    request: ReasoningRequest, result: ReasoningResult, extractor_version: str
) -> SemanticCacheBinding:
    unique = {(item.source.id, item.source_hash): item.source for item in request.excerpts}
    sources = [CacheSourceBinding(source=unique[key], source_hash=key[1]) for key in sorted(unique)]
    return SemanticCacheBinding(
        project_id=request.project_id,
        snapshot_id=request.snapshot_id,
        sources=sources,
        provider_identity=result.provider_identity,
        operation=request.operation,
        prompt_version=request.prompt_version,
        configuration_hash=request.configuration_hash,
        extractor_version=extractor_version,
    )


def materialize_provider_candidates(
    request: ReasoningRequest,
    result: ReasoningResult,
    ledger: d.SourceLedger,
    *,
    run_id: str,
    created_at: str,
    extractor_version: str,
) -> SemanticCandidateSet:
    """Turn a validated provider result into non-normative review candidates."""

    binding = _binding(request, result, extractor_version)
    common = dict(
        id=f"semantic-candidates.{hashlib.sha256((canonical_hash(result) + semantic_cache_key(binding)).encode()).hexdigest()[:24]}",
        project_id=request.project_id,
        snapshot_id=request.snapshot_id,
        request=d.Ref(
            id=request.id, project_id=request.project_id, snapshot_id=request.snapshot_id
        ),
        request_hash=canonical_hash(request),
        result=d.Ref(id=result.id, project_id=result.project_id, snapshot_id=result.snapshot_id),
        result_hash=canonical_hash(result),
        cache_binding=binding,
        cache_key=semantic_cache_key(binding),
    )
    if (
        not same_scope(request, result)
        or not same_scope(request, ledger)
        or result.request_hash != canonical_hash(request)
    ):
        return SemanticCandidateSet(
            **common,
            status="REJECTED",
            candidates=[],
            limitations=["Input artifact binding is invalid."],
        )
    sources = {source.id: source for source in ledger.sources}
    excerpt_by_id = {excerpt.id: excerpt for excerpt in request.excerpts}
    stale = any(
        (source := sources.get(excerpt.source.id)) is None
        or source.content_hash != excerpt.source_hash
        or source.study_status != "STUDIED"
        or source.read_integrity != "COMPLETE"
        or source.lifecycle in {"superseded", "deprecated", "archived"}
        for excerpt in request.excerpts
    )
    if stale or not validate_ledger(ledger).valid:
        return SemanticCandidateSet(
            **common,
            status="STALE_INPUT",
            candidates=[],
            limitations=["Source identity, lifecycle, or completeness no longer validates."],
        )
    if result.status == "NOT_REQUESTED":
        return SemanticCandidateSet(**common, status="NOT_REQUESTED", candidates=[])
    if result.status in {"FAILED", "TIMED_OUT"}:
        return SemanticCandidateSet(
            **common,
            status="BLOCKED_PROVIDER",
            candidates=[],
            limitations=[result.failure or "Provider unavailable."],
        )
    if result.status == "REJECTED":
        return SemanticCandidateSet(
            **common,
            status="REJECTED",
            candidates=[],
            limitations=[result.failure or "Provider result rejected."],
        )
    candidates: list[SemanticCandidate] = []
    for index, proposal in enumerate(result.proposals):
        evidence: list[CandidateEvidence] = []
        for excerpt_id in proposal.source_excerpt_ids:
            excerpt = excerpt_by_id[excerpt_id]
            source = sources[excerpt.source.id]
            evidence.append(
                CandidateEvidence(
                    excerpt=d.Ref(
                        id=excerpt.id,
                        project_id=excerpt.project_id,
                        snapshot_id=excerpt.snapshot_id,
                    ),
                    source=excerpt.source,
                    source_hash=excerpt.source_hash,
                    location=excerpt.location,
                    span=excerpt.span,
                    authority_class=source.authority_class,
                    source_lifecycle=source.lifecycle,
                )
            )
        seed = json.dumps(
            [common["result_hash"], index, proposal.model_dump(mode="json")], sort_keys=True
        )
        candidates.append(
            SemanticCandidate(
                id=f"semantic-candidate.{hashlib.sha256(seed.encode()).hexdigest()[:24]}",
                project_id=request.project_id,
                snapshot_id=request.snapshot_id,
                candidate_type=proposal.candidate_type,
                statement=proposal.statement,
                structured_value=proposal.structured_value,
                evidence=evidence,
                interpretation=proposal.interpretation,
                confidence=proposal.confidence,
                inferred=True,
                producer="PROVIDER",
                provider_identity=result.provider_identity,
                operation=request.operation,
                prompt_version=request.prompt_version,
                configuration_hash=request.configuration_hash,
                extractor_version=extractor_version,
                run_id=run_id,
                created_at=created_at,
                review_state="BLOCKED_SOURCE"
                if proposal.interpretation == "unresolved"
                else "REVIEW_REQUIRED",
            )
        )
    status: CandidateSetStatus = "PARTIAL" if result.status == "PARTIAL" else "READY_FOR_REVIEW"
    limitations = [result.failure] if result.failure else []
    return SemanticCandidateSet(
        **common, status=status, candidates=candidates, limitations=limitations
    )


def validate_candidate_set(
    artifact: SemanticCandidateSet,
    request: ReasoningRequest,
    result_record: ReasoningResult,
    ledger: d.SourceLedger,
) -> Result:
    result = Result()
    if not all(same_scope(artifact, item) for item in (request, result_record, ledger)):
        result.add("SEM_SCOPE", artifact, "Semantic artifacts cross project or snapshot scope.")
    if artifact.request_hash != canonical_hash(request) or artifact.result_hash != canonical_hash(
        result_record
    ):
        result.add("SEM_STALE_BINDING", artifact, "Semantic input hash binding is stale.")
    expected_binding = _binding(request, result_record, artifact.cache_binding.extractor_version)
    if artifact.cache_binding != expected_binding or artifact.cache_key != semantic_cache_key(
        expected_binding
    ):
        result.add("SEM_CACHE_BINDING", artifact, "Semantic cache binding is not exact.")
    sources = {source.id: source for source in ledger.sources}
    for candidate in artifact.candidates:
        for evidence in candidate.evidence:
            source = sources.get(evidence.source.id)
            if source is None or source.content_hash != evidence.source_hash:
                result.add("SEM_SOURCE_STALE", candidate, "Candidate source identity is stale.")
            elif (evidence.authority_class, evidence.source_lifecycle) != (
                source.authority_class,
                source.lifecycle,
            ):
                result.add(
                    "SEM_AUTHORITY_TAMPER",
                    candidate,
                    "Candidate source authority was not copied from the ledger.",
                )
    return result
