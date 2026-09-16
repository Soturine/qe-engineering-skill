from qe_skill.clarification import questions_from_normalization
from qe_skill.normalization import normalize_candidate_set
from tests.normalization_helpers import constraint, prepared, simple_meaning


def test_semantic_failure_generates_unanswered_ptbr_clarification_with_provenance() -> None:
    model, request, result, candidates = prepared(
        "O usuário não pode autenticar em até 30 s.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="authenticate",
            capability_surface="autenticar",
            modality="MAY",
            polarity="POSITIVE",
            constraints=[
                constraint(
                    kind="maximum_duration", operator="LE", value=30, surface="30 s", unit="s"
                )
            ],
        ),
        source_language="pt-BR",
    )
    model.ledger.manifest.project_locale = "pt-BR"
    model.ledger.manifest.output_language = "pt-BR"
    normalization = normalize_candidate_set(candidates, request, result, model.ledger)
    questions = questions_from_normalization(normalization, candidates)
    assert questions.output_language == "pt-BR"
    assert questions.questions
    question = next(item for item in questions.questions if item.category == "MODALITY_MISMATCH")
    assert question.question.startswith("Qual modalidade")
    assert question.reason.startswith("A modalidade normalizada")
    assert question.sources[0].id == "source"
    assert question.affected[0].id == candidates.candidates[0].id
    assert question.answer is None and question.status == "OPEN"
    assert not questions.answers_fabricated and not question.authority_changed
