from typing import Any

from qe_skill.reasoning import (
    EvidenceExcerpt,
    ProviderIdentity,
    ProviderProposal,
    ProviderResponse,
    ReasoningRequest,
    StaticReasoningProvider,
    run_reasoning,
)
from qe_skill.semantic import materialize_provider_candidates
from tests.helpers import minimal


def concept(label: str, surface: str) -> dict[str, object]:
    return {
        "label": label,
        "surface_forms": [surface],
        "evidence": [{"id": "excerpt", "project_id": "synthetic", "snapshot_id": "v1"}],
    }


def alias(surface: str, label: str) -> dict[str, object]:
    return {
        "alias": surface,
        "canonical_label": label,
        "evidence": [{"id": "excerpt", "project_id": "synthetic", "snapshot_id": "v1"}],
    }


def grounded_term(role: str, label: str, surface: str) -> dict[str, object]:
    return {"role": role, **concept(label, surface)}


def constraint(
    *, kind: str, operator: str, value: object, surface: str, unit: str | None = None
) -> dict[str, object]:
    return {
        "kind": kind,
        "operator": operator,
        "value": value,
        "unit": unit,
        "surface_form": surface,
        "evidence": [{"id": "excerpt", "project_id": "synthetic", "snapshot_id": "v1"}],
    }


def simple_meaning(
    *,
    actor_label: str | None,
    actor_surface: str | None,
    capability_label: str,
    capability_surface: str,
    modality: str,
    polarity: str = "POSITIVE",
    record_kind: str = "CLAIM",
    constraints: list[dict[str, object]] | None = None,
    terms: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    aliases = [alias(capability_surface, capability_label)]
    for term in terms or []:
        label = str(term["label"])
        surface = str(term["surface_forms"][0])
        if label.casefold() != surface.casefold():
            aliases.append(alias(surface, label))
    actor = None
    if actor_label and actor_surface:
        actor = concept(actor_label, actor_surface)
        if actor_label.casefold() != actor_surface.casefold():
            aliases.append(alias(actor_surface, actor_label))
    return {
        "record_kind": record_kind,
        "actor": actor,
        "capability": concept(capability_label, capability_surface),
        "intent": None,
        "modality": modality,
        "polarity": polarity,
        "constraints": constraints or [],
        "aliases": aliases,
        "terms": terms or [],
    }


def meaning(
    *,
    actor_label: str = "user",
    actor_surface: str = "customer",
    modality: str = "MUST",
    polarity: str = "POSITIVE",
    seconds: int = 5,
    record_kind: str = "CLAIM",
    include_actor_alias: bool = True,
    terms: list[dict[str, object]] | None = None,
) -> dict[str, Any]:
    aliases = [alias("authenticate", "authentication/login")]
    if include_actor_alias:
        aliases.append(alias(actor_surface, actor_label))
    return {
        "record_kind": record_kind,
        "actor": concept(actor_label, actor_surface),
        "capability": concept("authentication/login", "authenticate"),
        "intent": None,
        "modality": modality,
        "polarity": polarity,
        "constraints": [
            {
                "kind": "maximum_duration",
                "operator": "LE",
                "value": seconds,
                "unit": "seconds",
                "surface_form": f"{seconds} seconds",
                "evidence": [{"id": "excerpt", "project_id": "synthetic", "snapshot_id": "v1"}],
            }
        ],
        "aliases": aliases,
        "terms": terms or [],
    }


def prepared(
    text: str,
    normalized: dict[str, Any] | None,
    *,
    source_language: str = "und",
    source_id: str = "source",
    authority_class: str = "CONTRACT",
    lifecycle: str = "approved",
    provider_name: str = "static",
    confidence: float = 0.5,
):
    model = minimal()
    model.ledger.sources[0].id = source_id
    model.ledger.sources[0].authority_class = authority_class  # type: ignore[assignment]
    model.ledger.sources[0].lifecycle = lifecycle  # type: ignore[assignment]
    model.ledger.manifest.scope[0].source.id = source_id
    excerpt = EvidenceExcerpt(
        id="excerpt",
        project_id="synthetic",
        snapshot_id="v1",
        source=model.ledger.manifest.scope[0].source,
        source_hash="a" * 64,
        location="synthetic clause",
        text=text,
        source_language=source_language,
    )
    request = ReasoningRequest(
        id="request",
        project_id="synthetic",
        snapshot_id="v1",
        operation="EXTRACT",
        excerpts=[excerpt],
        prompt_version="normalization-v1",
        configuration_hash="b" * 64,
    )
    identity = ProviderIdentity(
        provider=provider_name, model="fixture", model_version="1", adapter_version="1"
    )
    structured_value = {"normalization": normalized} if normalized is not None else {}
    response = ProviderResponse(
        status="COMPLETE",
        proposals=[
            ProviderProposal(
                candidate_type="semantic_normalization_candidate",
                statement=text,
                structured_value=structured_value,
                source_excerpt_ids=["excerpt"],
                confidence=confidence,
            )
        ],
    )
    result = run_reasoning(request, StaticReasoningProvider(identity, {"EXTRACT": response}))
    candidates = materialize_provider_candidates(
        request,
        result,
        model.ledger,
        run_id="run-h3",
        created_at="2026-09-15T00:00:00Z",
        extractor_version="h3-v1",
    )
    return model, request, result, candidates
