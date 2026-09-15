from qe_skill.reasoning import (
    EvidenceExcerpt,
    ProviderIdentity,
    ProviderProposal,
    ProviderResponse,
    ReasoningRequest,
    StaticReasoningProvider,
    run_reasoning,
)
from qe_skill.semantic import (
    materialize_provider_candidates,
    semantic_cache_key,
    validate_candidate_set,
)
from tests.helpers import minimal


def inputs(*, confidence: float = 0.99):
    model = minimal()
    excerpt = EvidenceExcerpt(
        id="excerpt",
        project_id="synthetic",
        snapshot_id="v1",
        source=model.ledger.manifest.scope[0].source,
        source_hash="a" * 64,
        location="clause 1",
        text="Synthetic evidence remains untrusted input.",
    )
    request = ReasoningRequest(
        id="request",
        project_id="synthetic",
        snapshot_id="v1",
        operation="EXTRACT",
        excerpts=[excerpt],
        prompt_version="prompt-1",
        configuration_hash="b" * 64,
    )
    identity = ProviderIdentity(
        provider="static", model="fixture", model_version="1", adapter_version="1"
    )
    response = ProviderResponse(
        status="COMPLETE",
        proposals=[
            ProviderProposal(
                candidate_type="requirement_candidate",
                statement="A candidate, not an authorized contract.",
                source_excerpt_ids=["excerpt"],
                confidence=confidence,
            )
        ],
    )
    result = run_reasoning(request, StaticReasoningProvider(identity, {"EXTRACT": response}))
    return model, request, result


def materialized():
    model, request, result = inputs()
    artifact = materialize_provider_candidates(
        request,
        result,
        model.ledger,
        run_id="run-1",
        created_at="2026-01-01T00:00:00Z",
        extractor_version="1",
    )
    return model, request, result, artifact


def test_provider_confidence_cannot_self_authorize_candidate() -> None:
    model, request, result, artifact = materialized()
    candidate = artifact.candidates[0]
    assert artifact.status == "READY_FOR_REVIEW"
    assert candidate.confidence == 0.99
    assert candidate.normative is candidate.authority_promoted is False
    assert candidate.inferred is True and candidate.review_state == "REVIEW_REQUIRED"
    assert candidate.evidence[0].authority_class == model.ledger.sources[0].authority_class
    assert validate_candidate_set(artifact, request, result, model.ledger).valid


def test_source_mutation_invalidates_candidates_and_cache_identity() -> None:
    model, request, result = inputs()
    mutated = model.ledger.model_copy(deep=True)
    mutated.sources[0].content_hash = "c" * 64
    artifact = materialize_provider_candidates(
        request,
        result,
        mutated,
        run_id="run-1",
        created_at="2026-01-01T00:00:00Z",
        extractor_version="1",
    )
    assert artifact.status == "STALE_INPUT" and artifact.candidates == []

    _, request2, result2 = inputs()
    request2.excerpts[0].source_hash = "c" * 64
    changed = materialize_provider_candidates(
        request2,
        result2,
        mutated,
        run_id="run-1",
        created_at="2026-01-01T00:00:00Z",
        extractor_version="1",
    )
    assert semantic_cache_key(artifact.cache_binding) != semantic_cache_key(changed.cache_binding)


def test_cache_binding_changes_for_material_provider_and_prompt_inputs() -> None:
    _, _, _, artifact = materialized()
    original = artifact.cache_key
    assert original == semantic_cache_key(artifact.cache_binding)
    changed = artifact.cache_binding.model_copy(deep=True)
    changed.prompt_version = "prompt-2"
    assert semantic_cache_key(changed) != original
    changed = artifact.cache_binding.model_copy(deep=True)
    assert changed.provider_identity is not None
    changed.provider_identity.model_version = "2"
    assert semantic_cache_key(changed) != original


def test_validator_detects_authority_and_hash_tampering() -> None:
    model, request, result, artifact = materialized()
    artifact.candidates[0].evidence[0].authority_class = "IMPLEMENTATION"
    artifact.cache_key = "f" * 64
    codes = {
        item.code for item in validate_candidate_set(artifact, request, result, model.ledger).issues
    }
    assert codes == {"SEM_AUTHORITY_TAMPER", "SEM_CACHE_BINDING"}


def test_deterministic_only_result_creates_no_semantic_candidate() -> None:
    model, request, _ = inputs()
    result = run_reasoning(request)
    artifact = materialize_provider_candidates(
        request,
        result,
        model.ledger,
        run_id="run-1",
        created_at="2026-01-01T00:00:00Z",
        extractor_version="1",
    )
    assert artifact.status == "NOT_REQUESTED" and artifact.candidates == []
