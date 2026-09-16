from qe_skill.normalization import detect_surface_signals, normalize_candidate_set
from tests.normalization_helpers import (
    constraint,
    grounded_term,
    meaning,
    prepared,
    simple_meaning,
)


def normalized(text: str, value: dict):
    model, request, result, candidates = prepared(text, value)
    return normalize_candidate_set(candidates, request, result, model.ledger)


def test_grounded_paraphrases_compare_equal_without_losing_source_wording() -> None:
    first = normalized("The customer must authenticate within 5 seconds.", meaning())
    second = normalized("Within 5 seconds, the customer is required to authenticate.", meaning())
    assert first.status == second.status == "COMPLETE"
    assert first.records[0].comparison_key == second.records[0].comparison_key
    assert first.records[0].original_statements != second.records[0].original_statements


def test_modal_mutation_does_not_collapse() -> None:
    required = normalized("The customer must authenticate within 5 seconds.", meaning())
    optional = normalized(
        "The customer may authenticate within 5 seconds.", meaning(modality="MAY")
    )
    assert required.records[0].comparison_key != optional.records[0].comparison_key


def test_numeric_constraint_mutation_does_not_collapse() -> None:
    five = normalized("The customer must authenticate within 5 seconds.", meaning())
    ten = normalized("The customer must authenticate within 10 seconds.", meaning(seconds=10))
    assert five.records[0].comparison_key != ten.records[0].comparison_key


def test_negation_mutation_does_not_collapse_or_disappear() -> None:
    positive = normalized("The customer must authenticate within 5 seconds.", meaning())
    negative = normalized(
        "The customer must not authenticate within 5 seconds.",
        meaning(modality="MUST_NOT", polarity="NEGATIVE"),
    )
    lost = normalized(
        "The customer must not authenticate within 5 seconds.",
        meaning(modality="MUST_NOT", polarity="POSITIVE"),
    )
    assert positive.records[0].comparison_key != negative.records[0].comparison_key
    assert lost.status == "REJECTED" and lost.issues[0].code == "NEGATION_LOST"


def test_record_kind_prevents_hypothesis_from_collapsing_into_decision() -> None:
    hypothesis = normalized(
        "The customer must authenticate within 5 seconds.", meaning(record_kind="HYPOTHESIS")
    )
    decision = normalized(
        "The customer must authenticate within 5 seconds.", meaning(record_kind="DECISION")
    )
    assert hypothesis.records[0].comparison_key != decision.records[0].comparison_key


def test_ptbr_required_and_permission_are_not_equivalent() -> None:
    required = normalized(
        "O usuário deve cadastrar um endereço.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="register_address",
            capability_surface="cadastrar um endereço",
            modality="MUST",
        ),
    )
    permitted = normalized(
        "O usuário pode cadastrar um endereço.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="register_address",
            capability_surface="cadastrar um endereço",
            modality="MAY",
        ),
    )
    assert required.records[0].comparison_key != permitted.records[0].comparison_key
    assert permitted.records[0].meaning.modality == "MAY"
    assert permitted.records[0].meaning.modality != "OPTIONAL"


def test_ptbr_negated_permission_does_not_collapse() -> None:
    allowed = normalized(
        "O usuário pode cancelar o pedido.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="cancel_order",
            capability_surface="cancelar o pedido",
            modality="MAY",
        ),
    )
    prohibited = normalized(
        "O usuário não pode cancelar o pedido.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="cancel_order",
            capability_surface="cancelar o pedido",
            modality="MUST_NOT",
            polarity="NEGATIVE",
        ),
    )
    assert allowed.records[0].comparison_key != prohibited.records[0].comparison_key


def test_ptbr_quantity_and_brazilian_number_forms_are_preserved() -> None:
    hundred = normalized(
        "O sistema aceita no máximo 100 registros.",
        simple_meaning(
            actor_label="system",
            actor_surface="sistema",
            capability_label="accept_records",
            capability_surface="aceita",
            modality="UNSPECIFIED",
            constraints=[constraint(kind="maximum_count", operator="LE", value=100, surface="100")],
        ),
    )
    thousand = normalized(
        "O sistema aceita no máximo 1.000 registros.",
        simple_meaning(
            actor_label="system",
            actor_surface="sistema",
            capability_label="accept_records",
            capability_surface="aceita",
            modality="UNSPECIFIED",
            constraints=[
                constraint(kind="maximum_count", operator="LE", value=1000, surface="1.000")
            ],
        ),
    )
    currency = normalized(
        "O sistema aceita R$ 1.250,90.",
        simple_meaning(
            actor_label="system",
            actor_surface="sistema",
            capability_label="accept_amount",
            capability_surface="aceita",
            modality="UNSPECIFIED",
            constraints=[
                constraint(
                    kind="maximum_amount",
                    operator="LE",
                    value="1250.90",
                    surface="R$ 1.250,90",
                    unit="BRL",
                )
            ],
        ),
    )
    assert hundred.records[0].comparison_key != thousand.records[0].comparison_key
    assert thousand.records[0].surface_guards.numeric_literals == ["1.000"]
    assert currency.records[0].surface_guards.numeric_literals == ["1.250,90"]


def test_ptbr_actor_state_optionality_and_recommendation_mutations_do_not_collapse() -> None:
    admin = normalized(
        "O administrador pode excluir o usuário.",
        simple_meaning(
            actor_label="administrator",
            actor_surface="administrador",
            capability_label="delete_user",
            capability_surface="excluir o usuário",
            modality="MAY",
        ),
    )
    customer = normalized(
        "O cliente pode excluir o usuário.",
        simple_meaning(
            actor_label="customer",
            actor_surface="cliente",
            capability_label="delete_user",
            capability_surface="excluir o usuário",
            modality="MAY",
        ),
    )
    approved = normalized(
        "O pedido deve ir de PENDENTE para APROVADO.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="transition_order",
            capability_surface="pedido deve ir",
            modality="MUST",
            terms=[grounded_term("STATE", "approved", "APROVADO")],
        ),
    )
    rejected = normalized(
        "O pedido deve ir de PENDENTE para REJEITADO.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="transition_order",
            capability_surface="pedido deve ir",
            modality="MUST",
            terms=[grounded_term("STATE", "rejected", "REJEITADO")],
        ),
    )
    mandatory = normalized(
        "O CPF é obrigatório.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="provide_cpf",
            capability_surface="CPF",
            modality="MUST",
        ),
    )
    optional = normalized(
        "O CPF é opcional.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="provide_cpf",
            capability_surface="CPF",
            modality="OPTIONAL",
        ),
    )
    recommended = normalized(
        "Recomenda-se utilizar MFA.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="use_mfa",
            capability_surface="utilizar MFA",
            modality="SHOULD",
        ),
    )
    required = normalized(
        "O sistema deve exigir MFA.",
        simple_meaning(
            actor_label="system",
            actor_surface="sistema",
            capability_label="use_mfa",
            capability_surface="exigir MFA",
            modality="MUST",
        ),
    )
    pairs = (
        (admin, customer),
        (approved, rejected),
        (mandatory, optional),
        (recommended, required),
    )
    assert all(
        left.records[0].comparison_key != right.records[0].comparison_key for left, right in pairs
    )


def test_ptbr_paraphrases_retain_actor_context_while_sharing_capability() -> None:
    user = normalized(
        "O usuário deve cadastrar um endereço.",
        simple_meaning(
            actor_label="user",
            actor_surface="usuário",
            capability_label="register_address",
            capability_surface="cadastrar um endereço",
            modality="MUST",
        ),
    )
    customer = normalized(
        "O cliente precisa cadastrar um endereço.",
        simple_meaning(
            actor_label="customer",
            actor_surface="cliente",
            capability_label="register_address",
            capability_surface="cadastrar um endereço",
            modality="MUST",
        ),
    )
    mandatory = normalized(
        "É obrigatório possuir endereço cadastrado.",
        simple_meaning(
            actor_label=None,
            actor_surface=None,
            capability_label="register_address",
            capability_surface="endereço cadastrado",
            modality="MUST",
        ),
    )
    assert (
        user.records[0].meaning.capability.label
        == customer.records[0].meaning.capability.label
        == mandatory.records[0].meaning.capability.label
    )
    assert user.records[0].meaning.actor.label != customer.records[0].meaning.actor.label
    assert user.records[0].original_statements[0].text.startswith("O usuário")


def test_mixed_portuguese_gherkin_preserves_unicode_and_technical_identifiers() -> None:
    text = (
        "Dado que o usuário possui role ADMIN\n"
        "Quando chamar POST /users\n"
        "Então a API deve retornar 201 com status CREATED."
    )
    artifact = normalized(
        text,
        simple_meaning(
            actor_label="administrator",
            actor_surface="ADMIN",
            capability_label="create_user",
            capability_surface="POST /users",
            modality="MUST",
            constraints=[constraint(kind="http_status", operator="EQ", value=201, surface="201")],
            terms=[
                grounded_term("TECHNICAL_IDENTIFIER", "admin_role", "role ADMIN"),
                grounded_term("STATE", "created", "CREATED"),
            ],
        ),
    )
    record = artifact.records[0]
    statement = record.original_statements[0]
    assert statement.source_language == "mixed"
    assert statement.text == text
    assert [marker.role for marker in record.surface_guards.gherkin_markers] == [
        "GIVEN",
        "WHEN",
        "THEN",
    ]
    assert (
        "/users" in statement.text and "CREATED" in statement.text and "usuário" in statement.text
    )

    english = normalized(
        "Given an authenticated user\n"
        "When POST /orders is called\n"
        "Then the status must be CREATED.",
        simple_meaning(
            actor_label="user",
            actor_surface="user",
            capability_label="create_order",
            capability_surface="POST /orders",
            modality="MUST",
            terms=[grounded_term("STATE", "created", "CREATED")],
        ),
    )
    assert [marker.language for marker in english.records[0].surface_guards.gherkin_markers] == [
        "en",
        "en",
        "en",
    ]


def test_ptbr_requested_mutation_vocabulary_is_semantically_distinct() -> None:
    samples = {
        "required": "O campo deve ser preenchido e é obrigatório.",
        "allowed": "O campo pode ser preenchido.",
        "forbidden": "O campo não pode ser preenchido.",
        "optional": "O campo é opcional.",
        "before": "A ação ocorre antes do evento.",
        "after": "A ação ocorre depois do evento.",
        "maximum": "O sistema aceita até 10 itens e no máximo 10 itens.",
        "minimum": "O sistema aceita no mínimo 10 itens.",
        "exclusive": "Somente ADMIN pode agir, exceto SUPPORT.",
        "thirty": "A operação termina em 30 s.",
        "sixty": "A operação termina em 60 s.",
    }
    roles = {
        name: {(item.category, item.semantic_role) for item in detect_surface_signals(text)}
        for name, text in samples.items()
    }
    assert ("MODALITY", "MUST") in roles["required"]
    assert ("MODALITY", "MAY") in roles["allowed"]
    assert ("MODALITY", "MUST_NOT") in roles["forbidden"]
    assert ("MODALITY", "OPTIONAL") in roles["optional"]
    assert ("TEMPORAL_ORDER", "BEFORE") in roles["before"]
    assert ("TEMPORAL_ORDER", "AFTER") in roles["after"]
    assert ("CONSTRAINT", "MAXIMUM") in roles["maximum"]
    assert ("CONSTRAINT", "MINIMUM") in roles["minimum"]
    assert {("CONSTRAINT", "ONLY"), ("CONSTRAINT", "EXCEPT")} <= roles["exclusive"]
    assert ("QUANTITY", "MEASURED_QUANTITY") in roles["thirty"]
    assert ("QUANTITY", "MEASURED_QUANTITY") in roles["sixty"]
