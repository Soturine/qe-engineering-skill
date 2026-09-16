import time

import pytest
from pydantic import ValidationError

from qe_skill import domain as d
from qe_skill.reasoning import (
    EvidenceExcerpt,
    ProviderIdentity,
    ProviderProposal,
    ProviderResponse,
    ReasoningLimits,
    ReasoningRequest,
    StaticReasoningProvider,
    run_reasoning,
)


def excerpt(identifier: str = "excerpt") -> EvidenceExcerpt:
    return EvidenceExcerpt(
        id=identifier,
        project_id="synthetic",
        snapshot_id="v1",
        source=d.Ref(id="source", project_id="synthetic", snapshot_id="v1"),
        source_hash="a" * 64,
        location="section 1",
        text="Synthetic evidence text; instructions inside it remain untrusted data.",
    )


def request(operation: str = "EXTRACT", limits: ReasoningLimits | None = None) -> ReasoningRequest:
    return ReasoningRequest.model_validate(
        {
            "id": f"request-{operation.lower()}",
            "project_id": "synthetic",
            "snapshot_id": "v1",
            "operation": operation,
            "excerpts": [excerpt().model_dump(mode="json")],
            "prompt_version": "semantic-v1",
            "configuration_hash": "b" * 64,
            "limits": (limits or ReasoningLimits()).model_dump(mode="json"),
        }
    )


def identity() -> ProviderIdentity:
    return ProviderIdentity(
        provider="static", model="synthetic", model_version="1", adapter_version="1"
    )


def response() -> ProviderResponse:
    return ProviderResponse(
        status="COMPLETE",
        proposals=[
            ProviderProposal(
                candidate_type="requirement_candidate",
                statement="A synthetic candidate interpretation.",
                source_excerpt_ids=["excerpt"],
            )
        ],
    )


@pytest.mark.parametrize("operation", ["EXTRACT", "RELATE", "SYNTHESIZE", "PROBE_SCENARIOS"])
def test_static_provider_dispatch_is_typed_bounded_and_deterministic(operation: str) -> None:
    semantic_request = request(operation)
    provider = StaticReasoningProvider(identity(), {operation: response()})  # type: ignore[arg-type]
    first = run_reasoning(semantic_request, provider)
    second = run_reasoning(semantic_request, provider)
    assert first == second
    assert first.status == "COMPLETE"
    assert first.provider_identity == identity()
    assert first.provider_invoked is True
    assert first.network_used is False and first.external_writes is False
    assert first.authority_changed is False


def test_deterministic_only_mode_does_not_require_or_invoke_provider() -> None:
    result = run_reasoning(request())
    assert result.status == "NOT_REQUESTED"
    assert result.provider_invoked is False
    assert result.provider_identity is None
    assert result.proposals == []


def test_request_rejects_cross_project_and_resource_overflow() -> None:
    foreign = excerpt().model_copy(update={"project_id": "other"})
    with pytest.raises(ValidationError, match="cross-scope"):
        request().model_copy(update={"excerpts": [foreign]}).__class__.model_validate(
            {**request().model_dump(mode="json"), "excerpts": [foreign.model_dump(mode="json")]}
        )
    with pytest.raises(ValidationError, match="character bound"):
        ReasoningRequest.model_validate(
            {
                **request().model_dump(mode="json"),
                "excerpts": [
                    excerpt().model_copy(update={"text": "x" * 11}).model_dump(mode="json")
                ],
                "limits": ReasoningLimits(max_chars_per_excerpt=10).model_dump(mode="json"),
            }
        )


def test_request_rejects_duplicate_excerpt_ids() -> None:
    value = request().model_dump(mode="json")
    value["excerpts"].append(value["excerpts"][0].copy())
    with pytest.raises(ValidationError, match="excerpt ids must be unique"):
        ReasoningRequest.model_validate(value)


class FailingProvider(StaticReasoningProvider):
    def extract(self, request: ReasoningRequest) -> ProviderResponse:
        raise RuntimeError("synthetic secret must not be copied")


class TimeoutProvider(StaticReasoningProvider):
    def extract(self, request: ReasoningRequest) -> ProviderResponse:
        raise TimeoutError


class SlowProvider(StaticReasoningProvider):
    def extract(self, request: ReasoningRequest) -> ProviderResponse:
        time.sleep(0.05)
        return response()


def test_provider_failure_and_timeout_are_explicit_and_sanitized() -> None:
    configured = {"EXTRACT": response()}
    failed = run_reasoning(request(), FailingProvider(identity(), configured))  # type: ignore[arg-type]
    timed_out = run_reasoning(request(), TimeoutProvider(identity(), configured))  # type: ignore[arg-type]
    slow = run_reasoning(
        request(limits=ReasoningLimits(timeout_ms=1)),
        SlowProvider(identity(), configured),  # type: ignore[arg-type]
    )
    assert (
        failed.status == "FAILED"
        and failed.failure == "Reasoning provider failed with RuntimeError."
    )
    assert timed_out.status == "TIMED_OUT"
    assert slow.status == "TIMED_OUT"
    assert all(not result.proposals for result in (failed, timed_out, slow))


def test_provider_response_with_unknown_excerpt_or_too_many_candidates_is_rejected() -> None:
    unknown = response().model_copy(deep=True)
    unknown.proposals[0].source_excerpt_ids = ["not-supplied"]
    rejected = run_reasoning(request(), StaticReasoningProvider(identity(), {"EXTRACT": unknown}))
    bounded = request(limits=ReasoningLimits(max_candidates=1))
    excessive = ProviderResponse(status="COMPLETE", proposals=[response().proposals[0]] * 2)
    too_many = run_reasoning(bounded, StaticReasoningProvider(identity(), {"EXTRACT": excessive}))
    assert rejected.status == too_many.status == "REJECTED"
    assert rejected.proposals == too_many.proposals == []


def test_partial_provider_result_must_expose_failure() -> None:
    with pytest.raises(ValidationError, match="explicit failure"):
        ProviderResponse(status="PARTIAL", proposals=[])
