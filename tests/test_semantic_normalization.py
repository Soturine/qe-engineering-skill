from qe_skill.normalization import (
    detect_source_language,
    normalize_candidate_set,
    validate_normalization_set,
)
from qe_skill.reasoning import run_reasoning
from qe_skill.semantic import materialize_provider_candidates
from tests.normalization_helpers import meaning, prepared


def test_normalization_preserves_original_provenance_and_aliases() -> None:
    model, request, result, candidates = prepared(
        "The customer must authenticate within 5 seconds.", meaning()
    )
    artifact = normalize_candidate_set(candidates, request, result, model.ledger)
    assert artifact.status == "COMPLETE"
    record = artifact.records[0]
    assert record.original_statements[0].text == request.excerpts[0].text
    assert record.original_statements[0].source_hash == "a" * 64
    assert record.meaning.actor is not None and record.meaning.actor.label == "user"
    assert record.meaning.aliases[1].alias == "customer"
    assert record.normative is record.authority_promoted is False
    assert record.inferred is True and record.review_state == "REVIEW_REQUIRED"
    assert validate_normalization_set(artifact, candidates, request, result, model.ledger).valid


def test_missing_normalization_is_an_explicit_rejection() -> None:
    model, request, result, candidates = prepared("Unstructured candidate text.", None)
    artifact = normalize_candidate_set(candidates, request, result, model.ledger)
    assert artifact.status == "REJECTED" and artifact.records == []
    assert [issue.code for issue in artifact.issues] == ["NORMALIZATION_MISSING"]


def test_canonical_label_requires_explicit_alias_relation() -> None:
    value = meaning(include_actor_alias=False)
    model, request, result, candidates = prepared(
        "The customer must authenticate within 5 seconds.", value
    )
    artifact = normalize_candidate_set(candidates, request, result, model.ledger)
    assert artifact.status == "REJECTED"
    assert artifact.issues[0].code == "ALIAS_RELATION_MISSING"


def test_actor_cannot_be_invented_without_literal_grounding() -> None:
    value = meaning(actor_label="user", actor_surface="administrator")
    model, request, result, candidates = prepared(
        "The service must authenticate within 5 seconds.", value
    )
    artifact = normalize_candidate_set(candidates, request, result, model.ledger)
    assert artifact.status == "REJECTED"
    assert artifact.issues[0].code == "GROUNDING_MISSING"


def test_tampered_normalization_fails_exact_reconstruction() -> None:
    model, request, result, candidates = prepared(
        "The customer must authenticate within 5 seconds.", meaning()
    )
    artifact = normalize_candidate_set(candidates, request, result, model.ledger)
    artifact.records[0].meaning.record_kind = "ORACLE"
    assert not validate_normalization_set(artifact, candidates, request, result, model.ledger).valid


def test_deterministic_only_path_remains_valid_without_provider() -> None:
    model, request, _, _ = prepared("The customer must authenticate within 5 seconds.", meaning())
    result = run_reasoning(request)
    candidates = materialize_provider_candidates(
        request,
        result,
        model.ledger,
        run_id="run-h3",
        created_at="2026-09-15T00:00:00Z",
        extractor_version="h3-v1",
    )
    artifact = normalize_candidate_set(candidates, request, result, model.ledger)
    assert artifact.status == "NOT_REQUESTED"
    assert artifact.records == [] and artifact.issues == []


def test_stale_h2_input_propagates_without_normalizing_old_meaning() -> None:
    model, request, result, _ = prepared(
        "The customer must authenticate within 5 seconds.", meaning()
    )
    stale_ledger = model.ledger.model_copy(deep=True)
    stale_ledger.sources[0].content_hash = "c" * 64
    candidates = materialize_provider_candidates(
        request,
        result,
        stale_ledger,
        run_id="run-h3",
        created_at="2026-09-15T00:00:00Z",
        extractor_version="h3-v1",
    )
    artifact = normalize_candidate_set(candidates, request, result, stale_ledger)
    assert artifact.status == "STALE_INPUT"
    assert artifact.records == []


def test_declared_and_bounded_language_are_preserved_without_translation() -> None:
    text = "O usuário deve autenticar em até 5 segundos."
    value = meaning(actor_surface="usuário")
    value["capability"]["surface_forms"] = ["autenticar"]
    value["aliases"][0]["alias"] = "autenticar"
    value["constraints"][0]["surface_form"] = "5 segundos"
    model, request, result, candidates = prepared(text, value, source_language="pt-BR")
    model.ledger.manifest.project_locale = "pt-BR"
    model.ledger.manifest.output_language = "pt-BR"
    artifact = normalize_candidate_set(candidates, request, result, model.ledger)
    statement = artifact.records[0].original_statements[0]
    assert statement.text == text
    assert statement.source_language == "pt-BR"
    assert statement.language_method == "DECLARED"
    assert artifact.project_locale == artifact.output_language == "pt-BR"
    english_output = normalize_candidate_set(
        candidates, request, result, model.ledger, output_language="en"
    )
    assert english_output.output_language == "en"
    assert english_output.id != artifact.id
    assert detect_source_language(text) == ("pt-BR", "HIGH")


def test_language_detection_is_bounded_and_non_blocking() -> None:
    assert detect_source_language("opaque_identifier") == ("und", "LOW")
    assert detect_source_language(
        "O usuário realiza login em POST /auth/login e recebe access_token."
    ) == ("mixed", "HIGH")
