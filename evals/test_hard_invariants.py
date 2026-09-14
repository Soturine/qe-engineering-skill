import json
from pathlib import Path

import pytest

from evals.build_fixtures import serialized
from qe_skill import domain as d
from qe_skill.integrity import validate_project_model
from qe_skill.validation import validate_oracle
from tests.helpers import minimal, reference, representative

FIXTURES = sorted(Path("evals/fixtures").glob("*.json"))


@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: p.stem)
def test_corpus_outcomes(path: Path) -> None:
    fixture = json.loads(path.read_text(encoding="utf-8"))
    model = d.ProjectModel.model_validate(fixture["model"])
    before = model.model_dump_json()
    result = validate_project_model(model)
    errors = {i.code for i in result.issues if i.severity == "error"}
    assert bool(errors) == bool(fixture["expected_error_codes"]), result.issues
    assert set(fixture["expected_error_codes"]) <= errors
    assert model.model_dump_json() == before, "Validation must preserve historical artifacts."


def test_corpus_is_reproducible_and_nonempty() -> None:
    expected = serialized()
    assert len(FIXTURES) == len(expected) == 11
    for path in FIXTURES:
        assert path.read_text(encoding="utf-8") == expected[path.stem]


@pytest.mark.parametrize("invariant", ["missing", "inferred", "implementation", "summary", "stale"])
def test_risk_cannot_launder_unsupported_invariant(invariant: str) -> None:
    model = minimal()
    model.claims[0].origin = "RISK"
    model.oracles[0].origin = "RISK"
    claim = model.claims[0].model_copy(deep=True)
    claim.id = "invariant-claim"
    claim.origin = "CONTRACT"
    model.claims.append(claim)
    model.oracles[0].invariant_claim = reference(claim.id)
    if invariant == "missing":
        model.claims.pop()
    elif invariant == "inferred":
        claim.inferred = True
    elif invariant == "implementation":
        claim.origin = "IMPLEMENTATION"
    elif invariant == "summary":
        model.ledger.sources[0].primary = False
    else:
        claim.evidence[0].source_hash = "f" * 64
    assert not validate_oracle(model.oracles[0], model).valid


def test_valid_policy_backed_risk_preserves_origin() -> None:
    model = minimal()
    supporting = model.claims[0].model_copy(deep=True)
    supporting.id = "policy-backed"
    model.claims.append(supporting)
    model.claims[0].origin = "RISK"
    model.oracles[0].origin = "RISK"
    model.oracles[0].invariant_claim = reference("policy-backed")
    assert validate_oracle(model.oracles[0], model).valid
    assert model.oracles[0].origin == "RISK"


def test_unresolved_conflict_blocks_even_standalone_normative_oracle() -> None:
    model = representative()
    conflict = d.Conflict(
        id="conflict",
        project_id=model.project_id,
        snapshot_id=model.snapshot_id,
        name="Synthetic conflict",
        claims=[],
        conflicting_claims=[reference("claim"), reference("instruction-1")],
        affected=[],
        status="unresolved",
    )
    model.nodes.append(conflict)
    assert "ORACLE_CONFLICT" in {i.code for i in validate_oracle(model.oracles[0], model).issues}
    conflict.status = "resolved"
    assert "ORACLE_CONFLICT" in {i.code for i in validate_oracle(model.oracles[0], model).issues}


def test_role_permission_mapping_cannot_be_guessed() -> None:
    model = representative()
    mapping = next(node for node in model.nodes if isinstance(node, d.ActorMapping))
    mapping.status = "proposed"
    assert "READY_ACTOR_MAPPING" in {i.code for i in validate_project_model(model).issues}


def test_stale_snapshot_and_deleted_sole_support_fail_closed() -> None:
    for mutation in ("snapshot", "delete"):
        model = representative()
        if mutation == "snapshot":
            model.snapshot_id = "next"
        else:
            model.ledger.sources.clear()
        assert not validate_project_model(model).valid


def test_model_metadata_cannot_bypass_deterministic_gate() -> None:
    model = minimal()
    for provider in ("synthetic-provider-a", "synthetic-provider-b"):
        model.claims[0].extraction.provider = provider
        model.claims[0].extraction.model = "synthetic-model"
        model.claims[0].inferred = True
        assert not validate_oracle(model.oracles[0], model).valid
