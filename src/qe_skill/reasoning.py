"""Bounded provider-neutral semantic reasoning boundary for M4.

Provider output is untrusted candidate material. This module records invocation and failure
semantics; it does not promote candidates into Project Model facts or normative oracles.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections.abc import Mapping
from typing import Literal, Protocol

from pydantic import Field, JsonValue, model_validator

from qe_skill import domain as d

ReasoningOperation = Literal["EXTRACT", "RELATE", "SYNTHESIZE", "PROBE_SCENARIOS"]
ReasoningStatus = Literal["NOT_REQUESTED", "COMPLETE", "PARTIAL", "FAILED", "TIMED_OUT", "REJECTED"]


class ReasoningLimits(d.Record):
    max_excerpts: int = Field(default=64, ge=1, le=1_000)
    max_chars_per_excerpt: int = Field(default=20_000, ge=1, le=1_000_000)
    max_total_chars: int = Field(default=200_000, ge=1, le=5_000_000)
    max_candidates: int = Field(default=200, ge=1, le=10_000)
    timeout_ms: int = Field(default=30_000, ge=1, le=600_000)


class ProviderIdentity(d.Record):
    provider: d.Text
    model: d.Text
    model_version: d.Text
    adapter_version: d.Text


class EvidenceExcerpt(d.Artifact):
    source: d.Ref
    source_hash: d.Digest
    location: d.Text
    span: d.Ref | None = None
    text: d.Text

    @model_validator(mode="after")
    def validate_scope(self) -> EvidenceExcerpt:
        for ref in (self.source, self.span):
            if ref is not None and (
                ref.project_id != self.project_id or ref.snapshot_id != self.snapshot_id
            ):
                raise ValueError("cross-scope evidence excerpt reference")
        return self


class ProviderProposal(d.Record):
    candidate_type: d.Text
    statement: d.Text | None = None
    structured_value: dict[str, JsonValue] = Field(default_factory=dict)
    source_excerpt_ids: list[d.Text] = Field(min_length=1)
    inferred: Literal[True] = True

    @model_validator(mode="after")
    def validate_content(self) -> ProviderProposal:
        if self.statement is None and not self.structured_value:
            raise ValueError("provider proposal requires statement or structured value")
        return self


class ReasoningRequest(d.Artifact):
    operation: ReasoningOperation
    excerpts: list[EvidenceExcerpt] = Field(min_length=1)
    supported_facts: list[d.Ref] = Field(default_factory=list)
    prompt_version: d.Text
    configuration_hash: d.Digest
    limits: ReasoningLimits = Field(default_factory=ReasoningLimits)

    @model_validator(mode="after")
    def validate_scope_and_bounds(self) -> ReasoningRequest:
        if len(self.excerpts) > self.limits.max_excerpts:
            raise ValueError("reasoning excerpt count exceeds configured bound")
        if any(len(excerpt.text) > self.limits.max_chars_per_excerpt for excerpt in self.excerpts):
            raise ValueError("reasoning excerpt exceeds configured character bound")
        if sum(len(excerpt.text) for excerpt in self.excerpts) > self.limits.max_total_chars:
            raise ValueError("reasoning request exceeds configured total character bound")
        if any(
            excerpt.project_id != self.project_id or excerpt.snapshot_id != self.snapshot_id
            for excerpt in self.excerpts
        ) or any(
            fact.project_id != self.project_id or fact.snapshot_id != self.snapshot_id
            for fact in self.supported_facts
        ):
            raise ValueError("cross-scope reasoning input")
        return self


class ProviderResponse(d.Record):
    status: Literal["COMPLETE", "PARTIAL"]
    proposals: list[ProviderProposal]
    failure: d.Text | None = None
    network_used: bool = False

    @model_validator(mode="after")
    def validate_status(self) -> ProviderResponse:
        if self.status == "COMPLETE" and self.failure is not None:
            raise ValueError("complete provider response cannot contain a failure")
        if self.status == "PARTIAL" and self.failure is None:
            raise ValueError("partial provider response requires an explicit failure")
        return self


class ReasoningResult(d.Artifact):
    request: d.Ref
    request_hash: d.Digest
    operation: ReasoningOperation
    status: ReasoningStatus
    proposals: list[ProviderProposal]
    provider_identity: ProviderIdentity | None = None
    provider_invoked: bool
    failure: d.Text | None = None
    network_used: bool = False
    authority_changed: Literal[False] = False
    external_writes: Literal[False] = False

    @model_validator(mode="after")
    def validate_result_state(self) -> ReasoningResult:
        if (
            self.request.project_id != self.project_id
            or self.request.snapshot_id != self.snapshot_id
        ):
            raise ValueError("cross-scope reasoning result request")
        if self.status == "NOT_REQUESTED":
            if (
                self.provider_invoked
                or self.provider_identity is not None
                or self.failure is not None
                or self.proposals
                or self.network_used
            ):
                raise ValueError("not-requested result cannot claim provider activity")
        elif not self.provider_invoked or self.provider_identity is None:
            raise ValueError("provider result requires provider identity and invocation state")
        if self.status in {"FAILED", "TIMED_OUT", "REJECTED"} and self.failure is None:
            raise ValueError("failed reasoning result requires an explicit failure")
        if self.status in {"FAILED", "TIMED_OUT", "REJECTED"} and self.proposals:
            raise ValueError("failed reasoning result cannot retain unvalidated proposals")
        if self.status == "PARTIAL" and self.failure is None:
            raise ValueError("partial reasoning result requires an explicit failure")
        if self.status == "COMPLETE" and self.failure is not None:
            raise ValueError("complete reasoning result cannot contain a failure")
        return self


class ReasoningProvider(Protocol):
    @property
    def identity(self) -> ProviderIdentity: ...

    def extract(self, request: ReasoningRequest) -> ProviderResponse: ...

    def relate(self, request: ReasoningRequest) -> ProviderResponse: ...

    def synthesize(self, request: ReasoningRequest) -> ProviderResponse: ...

    def probe_scenarios(self, request: ReasoningRequest) -> ProviderResponse: ...


class StaticReasoningProvider:
    """Deterministic test/offline provider; it performs no inference or network access."""

    def __init__(
        self,
        identity: ProviderIdentity,
        responses: Mapping[ReasoningOperation, ProviderResponse],
    ) -> None:
        self._identity = identity
        self._responses = dict(responses)

    @property
    def identity(self) -> ProviderIdentity:
        return self._identity

    def _respond(
        self, request: ReasoningRequest, operation: ReasoningOperation
    ) -> ProviderResponse:
        if request.operation != operation:
            raise ValueError("reasoning method does not match request operation")
        response = self._responses.get(operation)
        if response is None:
            raise RuntimeError(f"No static response configured for {operation}.")
        return response.model_copy(deep=True)

    def extract(self, request: ReasoningRequest) -> ProviderResponse:
        return self._respond(request, "EXTRACT")

    def relate(self, request: ReasoningRequest) -> ProviderResponse:
        return self._respond(request, "RELATE")

    def synthesize(self, request: ReasoningRequest) -> ProviderResponse:
        return self._respond(request, "SYNTHESIZE")

    def probe_scenarios(self, request: ReasoningRequest) -> ProviderResponse:
        return self._respond(request, "PROBE_SCENARIOS")


def canonical_hash(value: d.Record) -> str:
    payload = json.dumps(
        value.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


def _result(
    request: ReasoningRequest,
    *,
    status: ReasoningStatus,
    proposals: list[ProviderProposal],
    identity: ProviderIdentity | None,
    invoked: bool,
    failure: str | None = None,
    network_used: bool = False,
) -> ReasoningResult:
    request_hash = canonical_hash(request)
    identity_key = identity.model_dump(mode="json") if identity else None
    result_key = json.dumps(
        [request_hash, status, identity_key, [item.model_dump(mode="json") for item in proposals]],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return ReasoningResult(
        id=f"reasoning-result.{hashlib.sha256(result_key.encode()).hexdigest()[:24]}",
        project_id=request.project_id,
        snapshot_id=request.snapshot_id,
        request=d.Ref(
            id=request.id, project_id=request.project_id, snapshot_id=request.snapshot_id
        ),
        request_hash=request_hash,
        operation=request.operation,
        status=status,
        proposals=proposals,
        provider_identity=identity,
        provider_invoked=invoked,
        failure=failure,
        network_used=network_used,
    )


def run_reasoning(
    request: ReasoningRequest, provider: ReasoningProvider | None = None
) -> ReasoningResult:
    """Invoke an optional provider and convert every failure into an explicit result."""

    if provider is None:
        return _result(
            request,
            status="NOT_REQUESTED",
            proposals=[],
            identity=None,
            invoked=False,
        )
    identity = provider.identity
    started = time.monotonic()
    try:
        methods = {
            "EXTRACT": provider.extract,
            "RELATE": provider.relate,
            "SYNTHESIZE": provider.synthesize,
            "PROBE_SCENARIOS": provider.probe_scenarios,
        }
        response = methods[request.operation](request)
    except TimeoutError:
        return _result(
            request,
            status="TIMED_OUT",
            proposals=[],
            identity=identity,
            invoked=True,
            failure="Reasoning provider timed out.",
        )
    except Exception as error:  # provider boundary must fail closed with a structured result
        return _result(
            request,
            status="FAILED",
            proposals=[],
            identity=identity,
            invoked=True,
            failure=f"Reasoning provider failed with {type(error).__name__}.",
        )
    if not isinstance(response, ProviderResponse):
        return _result(
            request,
            status="REJECTED",
            proposals=[],
            identity=identity,
            invoked=True,
            failure="Provider returned an invalid response contract.",
        )
    elapsed_ms = (time.monotonic() - started) * 1_000
    if elapsed_ms > request.limits.timeout_ms:
        return _result(
            request,
            status="TIMED_OUT",
            proposals=[],
            identity=identity,
            invoked=True,
            failure="Reasoning provider exceeded the configured timeout.",
            network_used=response.network_used,
        )
    known_excerpts = {excerpt.id for excerpt in request.excerpts}
    if len(response.proposals) > request.limits.max_candidates or any(
        not set(proposal.source_excerpt_ids) <= known_excerpts for proposal in response.proposals
    ):
        return _result(
            request,
            status="REJECTED",
            proposals=[],
            identity=identity,
            invoked=True,
            failure="Provider response violated candidate or provenance bounds.",
            network_used=response.network_used,
        )
    return _result(
        request,
        status=response.status,
        proposals=response.proposals,
        identity=identity,
        invoked=True,
        failure=response.failure,
        network_used=response.network_used,
    )
