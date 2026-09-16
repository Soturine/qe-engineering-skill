from qe_skill.adjudication import RelationInput, build_relation_graph, validate_relation_graph
from qe_skill.normalization import normalize_candidate_set
from tests.normalization_helpers import (
    grounded_term,
    meaning,
    prepared,
    simple_meaning,
)


def normalized_set(text: str, value: dict, **kwargs):
    model, request, result, candidates = prepared(text, value, **kwargs)
    return RelationInput(
        normalization=normalize_candidate_set(candidates, request, result, model.ledger),
        candidates=candidates,
        request=request,
        result=result,
        ledger=model.ledger,
    )


def relation(left, right):
    graph = build_relation_graph([left, right])
    assert graph.status == "COMPLETE" and len(graph.relations) == 1
    return graph, graph.relations[0], graph.adjudications[0]


def test_agreement_preserves_both_records_and_ignores_confidence() -> None:
    left = normalized_set(
        "The customer must authenticate within 5 seconds.",
        meaning(),
        source_id="requirement-a",
        confidence=0.1,
    )
    right = normalized_set(
        "Within 5 seconds, the customer is required to authenticate.",
        meaning(),
        source_id="requirement-b",
        confidence=0.99,
    )
    graph, edge, decision = relation(left, right)
    assert edge.relation == "CONSISTENT"
    assert edge.confidence_used_to_select_winner is False
    assert decision.outcome == "PRESERVE_BOTH" and decision.winner is None
    assert validate_relation_graph(graph, [left, right]).valid


def test_grounded_detail_is_a_refinement_not_a_silent_merge() -> None:
    base = normalized_set(
        "The customer must authenticate.",
        simple_meaning(
            actor_label="user",
            actor_surface="customer",
            capability_label="authentication/login",
            capability_surface="authenticate",
            modality="MUST",
        ),
        source_id="base",
    )
    detailed = normalized_set(
        "The customer must authenticate within 5 seconds.",
        meaning(),
        source_id="detail",
    )
    _, edge, decision = relation(base, detailed)
    assert edge.relation == "REFINEMENT"
    assert edge.refinement_record is not None
    assert edge.refinement_record.id == detailed.normalization.records[0].id
    assert decision.outcome == "RECORD_REFINEMENT" and decision.winner is None


def test_conflict_is_preserved_without_a_winner() -> None:
    required = normalized_set(
        "The customer must authenticate within 5 seconds.",
        meaning(),
        source_id="required",
    )
    optional = normalized_set(
        "The customer may authenticate within 5 seconds.",
        meaning(modality="MAY"),
        source_id="optional",
    )
    _, edge, decision = relation(required, optional)
    assert edge.relation == "CONFLICTING"
    assert decision.outcome == "PRESERVE_CONFLICT"
    assert decision.conflict_preserved is True and decision.winner is None
    assert decision.human_review_required is True
    assert decision.facts_promoted is decision.provider_self_authorized is False


def test_supersession_requires_explicit_lifecycle_evidence() -> None:
    old = normalized_set(
        "The customer must authenticate within 5 seconds.",
        meaning(),
        source_id="old",
    )
    # Editing a historical record is tampering, not evidence of a replacement relation.
    old.normalization.records[0].original_statements[0].source_lifecycle = "superseded"
    current = normalized_set(
        "Within 5 seconds, the customer is required to authenticate.",
        meaning(),
        source_id="current",
        lifecycle="approved",
    )
    graph = build_relation_graph([old, current])
    assert graph.status == "REJECTED" and not graph.relations


def test_authority_difference_is_visible_and_does_not_change_meaning() -> None:
    contract = normalized_set(
        "The customer must authenticate within 5 seconds.",
        meaning(),
        source_id="contract",
        authority_class="CONTRACT",
    )
    guidance = normalized_set(
        "Within 5 seconds, the customer is required to authenticate.",
        meaning(),
        source_id="guide",
        authority_class="GUIDANCE",
    )
    graph, edge, _ = relation(contract, guidance)
    assert edge.relation == "CONSISTENT"
    assert edge.authority_context.left_authority == ["CONTRACT"]
    assert edge.authority_context.right_authority == ["GUIDANCE"]
    edge.authority_context.left_authority = ["GUIDANCE"]
    assert not validate_relation_graph(graph, [contract, guidance]).valid


def test_matching_implementation_does_not_prove_a_deployment_instance() -> None:
    contract = normalized_set(
        "The customer must authenticate within 5 seconds.",
        meaning(),
        source_id="contract",
        authority_class="CONTRACT",
    )
    implementation = normalized_set(
        "Within 5 seconds, the customer is required to authenticate.",
        meaning(),
        source_id="implementation",
        authority_class="IMPLEMENTATION",
        lifecycle="active",
    )
    _, edge, decision = relation(contract, implementation)
    assert edge.relation == "CONSISTENT"
    assert edge.deployment_record is None
    assert decision.outcome == "PRESERVE_BOTH"


def test_provider_disagreement_requires_human_decision_regardless_of_confidence() -> None:
    claim = normalized_set(
        "The customer authentication policy applies.",
        simple_meaning(
            actor_label="user",
            actor_surface="customer",
            capability_label="authentication",
            capability_surface="authentication",
            modality="UNSPECIFIED",
            record_kind="CLAIM",
        ),
        provider_name="provider-a",
        confidence=0.99,
    )
    hypothesis = normalized_set(
        "The customer authentication policy applies.",
        simple_meaning(
            actor_label="user",
            actor_surface="customer",
            capability_label="authentication",
            capability_surface="authentication",
            modality="UNSPECIFIED",
            record_kind="HYPOTHESIS",
        ),
        provider_name="provider-b",
        confidence=0.1,
    )
    _, edge, decision = relation(claim, hypothesis)
    assert edge.relation == "HUMAN_DECISION_REQUIRED"
    assert decision.human_review_required is True and decision.winner is None


def test_ptbr_conflicting_confirmation_channels_remain_unresolved() -> None:
    sms = normalized_set(
        "O cliente deve confirmar por SMS.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="confirm_customer",
            capability_surface="confirmar",
            modality="MUST",
            terms=[grounded_term("VALUE", "sms", "SMS")],
        ),
        source_id="prd",
        authority_class="CONTRACT",
    )
    app = normalized_set(
        "SMS não será utilizado; confirmação será por aplicativo.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="confirm_customer",
            capability_surface="confirmação",
            modality="MUST_NOT",
            polarity="NEGATIVE",
            terms=[grounded_term("VALUE", "application", "aplicativo")],
        ),
        source_id="adr",
        authority_class="TECHNICAL_CONTRACT",
    )
    _, edge, decision = relation(sms, app)
    assert edge.relation == "CONFLICTING"
    assert decision.conflict_preserved is True and decision.winner is None


def test_unrelated_actor_or_capability_remains_ambiguous() -> None:
    first = normalized_set(
        "The customer must authenticate within 5 seconds.", meaning(), source_id="first"
    )
    second = normalized_set(
        "The administrator may delete users.",
        simple_meaning(
            actor_label="administrator",
            actor_surface="administrator",
            capability_label="delete_user",
            capability_surface="delete users",
            modality="MAY",
        ),
        source_id="second",
    )
    _, edge, decision = relation(first, second)
    assert edge.relation == "AMBIGUOUS"
    assert decision.outcome == "HUMAN_REVIEW_REQUIRED"


def test_tampered_authority_and_stale_sources_are_rejected() -> None:
    baseline = normalized_set(
        "The customer must authenticate within 5 seconds.", meaning(), source_id="a"
    )
    other = normalized_set(
        "The customer must authenticate within 5 seconds.", meaning(), source_id="b"
    )
    authority = baseline.model_copy(deep=True)
    authority.normalization.records[0].original_statements[0].authority_class = "GUIDANCE"
    stale = baseline.model_copy(deep=True)
    stale.ledger.sources[0].content_hash = "0" * 64
    scope = baseline.model_copy(deep=True)
    scope.normalization.records[0].project_id = "foreign"
    for changed in (authority, stale, scope):
        graph = build_relation_graph([changed, other])
        assert graph.status == "REJECTED" and not graph.relations


def test_numeric_difference_is_detected_without_a_relation_provider() -> None:
    left = normalized_set(
        "The customer must authenticate within 30 seconds.", meaning(seconds=30), source_id="a"
    )
    right = normalized_set(
        "The customer must authenticate within 60 seconds.", meaning(seconds=60), source_id="b"
    )
    _, edge, decision = relation(left, right)
    assert edge.relation == "CONFLICTING"
    assert decision.human_review_required and decision.winner is None
