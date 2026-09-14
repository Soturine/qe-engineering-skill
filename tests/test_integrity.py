import pytest

from qe_skill import domain as d
from qe_skill.integrity import validate_project_model, validate_test_case
from tests.helpers import ref, reference, representative


def test_representative_model_passes() -> None:
    result = validate_project_model(representative())
    assert result.valid, result.issues


@pytest.mark.parametrize("target", ["model", "ledger", "claim", "oracle", "node", "test"])
@pytest.mark.parametrize("dimension", ["project_id", "snapshot_id"])
def test_namespaces_on_all_artifacts(target: str, dimension: str) -> None:
    model = representative()
    artifact = {
        "model": model,
        "ledger": model.ledger,
        "claim": model.claims[0],
        "oracle": model.oracles[0],
        "node": model.nodes[0],
        "test": model.tests.test_cases[0],
    }[target]
    setattr(artifact, dimension, "foreign")
    assert not validate_project_model(model).valid


def test_duplicate_and_missing_ids_fail() -> None:
    model = representative()
    model.nodes.append(model.nodes[0].model_copy(deep=True))
    assert "MODEL_DUPLICATE_ID" in {i.code for i in validate_project_model(model).issues}
    model.nodes = [node for node in model.nodes if node.id != "actor"]
    assert "MODEL_MISSING_REF" in {i.code for i in validate_project_model(model).issues}


def test_wrong_reference_type_and_entity_are_rejected() -> None:
    model = representative()
    state = next(node for node in model.nodes if isinstance(node, d.State))
    state.entity = reference("entity-b")
    assert "MODEL_STATE_ENTITY" in {i.code for i in validate_project_model(model).issues}
    state.entity = reference("actor")
    assert "MODEL_REF_TYPE" in {i.code for i in validate_project_model(model).issues}


@pytest.mark.parametrize("mutation", ["unresolved", "invented", "inferred", "missing"])
def test_verified_path_requires_current_exact_provenance(mutation: str) -> None:
    model = representative()
    path = next(node for node in model.nodes if isinstance(node, d.VerifiedPath))
    if mutation == "unresolved":
        path.verification_status = "unresolved"
    elif mutation == "invented":
        path.steps[0].instruction = "Open an invented menu."
    elif mutation == "inferred":
        claim = next(c for c in model.claims if c.id == path.steps[0].claim.id)
        claim.inferred = True
    else:
        path.steps[0].claim = reference("missing")
    assert not validate_project_model(model).valid


def test_affected_conflict_blocks_ready_but_preserves_draft() -> None:
    model = representative()
    conflict = d.Conflict.model_validate(
        {
            **ref("conflict"),
            "name": "Synthetic conflict",
            "claims": [],
            "conflicting_claims": [ref("claim"), ref("instruction-1")],
            "affected": [ref("test")],
            "status": "unresolved",
        }
    )
    model.nodes.append(conflict)
    assert "READY_CONFLICT" in {i.code for i in validate_project_model(model).issues}
    model.tests.test_cases[0].readiness = "AMBIGUOUS"
    model.oracles[0].normative = False
    assert validate_project_model(model).valid
    conflict.status = "resolved"
    assert "MODEL_RESOLUTION" in {i.code for i in validate_project_model(model).issues}


@pytest.mark.parametrize("mutation", ["actor", "order", "expected", "action", "review", "partial"])
def test_invalid_manual_readiness(mutation: str) -> None:
    model = representative()
    test = model.tests.test_cases[0]
    if mutation == "actor":
        test.actor = None
    elif mutation == "order":
        test.steps[0].number = 2
    elif mutation == "expected":
        test.steps[0].expected_result = "Invented exact result"
    elif mutation == "action":
        test.steps[0].action.text = "Perform an unsupported action."
    elif mutation == "review":
        test.review_required = True
    else:
        model.ledger.manifest.completeness = "PARTIAL"
    assert not validate_test_case(test, model).valid


def test_exploratory_has_no_pass_fail() -> None:
    model = representative()
    test = model.tests.test_cases[0]
    test.origin = "EXPLORATORY"
    test.readiness = "EXPLORATORY_ONLY"
    test.steps = []
    assert not validate_test_case(test, model).valid
    test.pass_rule = None
    test.fail_rule = None
    assert validate_test_case(test, model).valid
