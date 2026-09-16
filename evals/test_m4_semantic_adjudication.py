from qe_skill.adjudication import RelationInput, build_relation_graph, validate_relation_graph
from qe_skill.normalization import normalize_candidate_set
from tests.normalization_helpers import grounded_term, meaning, prepared, simple_meaning
from tests.test_semantic_adjudication import provider_relation


def normalized_set(text: str, value: dict, **kwargs):
    model, request, result, candidates = prepared(text, value, **kwargs)
    return RelationInput(
        normalization=normalize_candidate_set(candidates, request, result, model.ledger),
        candidates=candidates,
        request=request,
        result=result,
        ledger=model.ledger,
    )


def test_authority_does_not_erase_ptbr_conflict() -> None:
    required = normalized_set(
        "O usuário deve cancelar o pedido.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="cancel_order",
            capability_surface="cancelar o pedido",
            modality="MUST",
        ),
        source_id="approved-prd",
        authority_class="CONTRACT",
    )
    prohibited = normalized_set(
        "O usuário não pode cancelar o pedido.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="cancel_order",
            capability_surface="cancelar o pedido",
            modality="MUST_NOT",
            polarity="NEGATIVE",
        ),
        source_id="implementation-note",
        authority_class="IMPLEMENTATION",
        lifecycle="active",
    )
    graph = build_relation_graph([required, prohibited])
    assert graph.relations[0].relation == "CONFLICTING"
    assert graph.adjudications[0].outcome == "PRESERVE_CONFLICT"
    assert graph.adjudications[0].winner is None


def test_provider_confidence_cannot_resolve_same_evidence_disagreement() -> None:
    first = normalized_set(
        "The authentication policy applies.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="authentication",
            capability_surface="authentication",
            modality="UNSPECIFIED",
            record_kind="CLAIM",
        ),
        provider_name="provider-high",
        confidence=1.0,
    )
    second = normalized_set(
        "The authentication policy applies.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="authentication",
            capability_surface="authentication",
            modality="UNSPECIFIED",
            record_kind="HYPOTHESIS",
        ),
        provider_name="provider-low",
        confidence=0.0,
    )
    graph = build_relation_graph([first, second])
    assert graph.relations[0].relation == "HUMAN_DECISION_REQUIRED"
    assert graph.adjudications[0].human_review_required is True
    assert graph.adjudications[0].provider_self_authorized is False


def test_ptbr_state_disagreement_is_a_preserved_conflict() -> None:
    approved = normalized_set(
        "O pedido deve mudar para APROVADO.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="transition_order",
            capability_surface="pedido deve mudar",
            modality="MUST",
            terms=[grounded_term("STATE", "approved", "APROVADO")],
        ),
        source_id="source-approved",
    )
    rejected = normalized_set(
        "O pedido deve mudar para REJEITADO.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="transition_order",
            capability_surface="pedido deve mudar",
            modality="MUST",
            terms=[grounded_term("STATE", "rejected", "REJEITADO")],
        ),
        source_id="source-rejected",
    )
    graph = build_relation_graph([approved, rejected])
    assert graph.relations[0].relation == "CONFLICTING"
    assert graph.adjudications[0].conflict_preserved is True


def test_cross_project_and_resource_overflow_fail_closed() -> None:
    sets = [
        normalized_set(
            "The customer must authenticate within 5 seconds.",
            meaning(),
            source_id=f"source-{index}",
        )
        for index in range(3)
    ]
    bounded = build_relation_graph(sets, max_records=2)
    assert bounded.status == "REJECTED" and bounded.relations == []

    foreign = sets[1].model_copy(deep=True)
    foreign.normalization.project_id = "foreign"
    isolated = build_relation_graph([sets[0], foreign])
    assert isolated.status == "REJECTED" and isolated.relations == []


def test_adjudication_tamper_is_detected_by_exact_reconstruction() -> None:
    left = normalized_set(
        "The customer must authenticate within 5 seconds.", meaning(), source_id="left"
    )
    right = normalized_set(
        "Within 5 seconds, the customer is required to authenticate.",
        meaning(),
        source_id="right",
    )
    graph = build_relation_graph([left, right])
    graph.adjudications[0].human_review_required = True
    assert not validate_relation_graph(graph, [left, right]).valid


def test_ptbr_provider_relation_stays_candidate_only() -> None:
    before = normalized_set(
        "O cliente pode cancelar o pedido antes do faturamento.",
        simple_meaning(
            actor_label="customer",
            actor_surface="cliente",
            capability_label="cancel_order",
            capability_surface="cancelar o pedido",
            modality="MAY",
        ),
        source_id="before",
    )
    paid = normalized_set(
        "Pedidos com pagamento confirmado não podem ser cancelados.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="cancel_order",
            capability_surface="cancelados",
            modality="MUST_NOT",
            polarity="NEGATIVE",
        ),
        source_id="paid",
    )
    candidate = provider_relation(before, paid, "CONFLICTING")
    graph = build_relation_graph([before, paid], relation_candidates=[candidate])
    assert graph.relations[0].provider_candidate_relation == "CONFLICTING"
    assert graph.relations[0].relation == "HUMAN_DECISION_REQUIRED"
    assert graph.adjudications[0].human_review_required
    assert graph.adjudications[0].winner is None
