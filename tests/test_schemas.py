import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from qe_skill.domain import Approval, Operation, Ref
from qe_skill.schemas import CONTRACTS, schema_text


@pytest.mark.parametrize("name", CONTRACTS)
def test_schemas_are_valid_and_reproducible(name: str) -> None:
    text = (Path("schemas/v1") / f"{name}.schema.json").read_text(encoding="utf-8")
    assert text == schema_text(name)
    Draft202012Validator.check_schema(json.loads(text))


def test_strict_reference_rejects_missing_namespace_and_extra_fields() -> None:
    with pytest.raises(ValidationError):
        Ref.model_validate({"id": "x", "project_id": "p"})
    with pytest.raises(ValidationError):
        Ref.model_validate({"id": "x", "project_id": "p", "snapshot_id": "s", "trust": True})


def test_approval_requires_attribution_and_exact_scope() -> None:
    with pytest.raises(ValidationError):
        Approval.model_validate({"id": "a", "project_id": "p", "snapshot_id": "s"})


def test_destructive_operation_not_in_normal_contract() -> None:
    with pytest.raises(ValidationError):
        Operation.model_validate({"kind": "delete", "id": "op"})
