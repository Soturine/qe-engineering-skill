import json
import subprocess
import sys
from pathlib import Path

import pytest

from qe_skill.cli import MAX_BYTES, main
from qe_skill.validation import digest
from tests.helpers import representative
from tests.test_trust import approved_promotion


@pytest.mark.parametrize(
    "command",
    ["validate-ledger", "validate-oracle", "validate-project-model", "validate-test-case"],
)
def test_commands_validate_real_artifacts(tmp_path: Path, capsys, command: str) -> None:
    model = representative()
    path = tmp_path / "input.json"
    artifact = model.ledger if command == "validate-ledger" else model
    path.write_text(artifact.model_dump_json(), encoding="utf-8")
    args = [command, str(path)]
    if command == "validate-oracle":
        args += ["--id", "oracle"]
    if command == "validate-test-case":
        args += ["--id", "test"]
    assert main(args) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["valid"] and not output["publication_authorized"]


@pytest.mark.parametrize(
    "payload,code",
    [
        ('{"id":"a","id":"b"}', "MODEL_DUPLICATE_KEY"),
        ('{"value":NaN}', "MODEL_JSON"),
        ("{broken", "MODEL_JSON"),
        ('{"$ref":"https://untrusted.invalid/schema"}', "MODEL_SCHEMA"),
        ("[" * 70 + "0" + "]" * 70, "SRC_INPUT_LIMIT"),
        (" " * (MAX_BYTES + 1), "SRC_INPUT_LIMIT"),
        (json.dumps([{}] * 2001), "SRC_INPUT_LIMIT"),
    ],
    ids=["duplicate-keys", "nan", "malformed", "remote-ref", "depth", "bytes", "record-count"],
)
def test_hostile_input_fails_structurally(tmp_path: Path, capsys, payload: str, code: str) -> None:
    path = tmp_path / "hostile.json"
    path.write_text(payload, encoding="utf-8")
    assert main(["validate-project-model", str(path)]) == 1
    assert json.loads(capsys.readouterr().out)["issues"][0]["code"] == code


def test_missing_file_reports_failure(tmp_path: Path, capsys) -> None:
    assert main(["validate-ledger", str(tmp_path / "absent.json")]) == 1
    assert json.loads(capsys.readouterr().out)["issues"][0]["code"] == "SRC_INPUT"


def test_invalid_oracle_exit_and_no_sensitive_statement_logging(tmp_path: Path) -> None:
    model = representative()
    model.oracles[0].statement = "SYNTHETIC_SECRET_CANARY"
    path = tmp_path / "invalid.json"
    path.write_text(model.model_dump_json(), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, "-m", "qe_skill.cli", "validate-oracle", str(path), "--id", "oracle"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 1
    assert "SYNTHETIC_SECRET_CANARY" not in completed.stdout + completed.stderr
    assert not json.loads(completed.stdout)["valid"]


def test_governed_approval_is_explicit_input(tmp_path: Path, capsys) -> None:
    model, _ = approved_promotion()
    model_path = tmp_path / "model.json"
    trust_path = tmp_path / "operator.json"
    model_path.write_text(model.model_dump_json(), encoding="utf-8")
    trust_path.write_text(
        json.dumps({"approved_record_hashes": [digest(model.approvals[0])]}), encoding="utf-8"
    )
    assert main(["validate-project-model", str(model_path)]) == 1
    capsys.readouterr()
    assert (
        main(["validate-project-model", str(model_path), "--trusted-approvals", str(trust_path)])
        == 0
    )
    assert not json.loads(capsys.readouterr().out)["publication_authorized"]


def test_prompt_injection_remains_inert(tmp_path: Path, capsys) -> None:
    from evals.build_fixtures import corpus

    model = corpus()["prompt-injection"][0]
    path = tmp_path / "injection.json"
    path.write_text(model.model_dump_json(), encoding="utf-8")
    assert main(["validate-project-model", str(path)]) == 0
    assert "SYNTHETIC_SECRET_CANARY" not in capsys.readouterr().out
    assert path.read_text(encoding="utf-8") == model.model_dump_json()
