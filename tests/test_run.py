import json
from pathlib import Path

import yaml

from qe_skill.cli import main
from qe_skill.reasoning import ProviderProposal, ProviderResponse
from qe_skill.run import execute_run


def test_agent_first_run_persists_bounded_handoff_and_human_outputs(tmp_path: Path) -> None:
    (tmp_path / "requisitos.md").write_text(
        "# Requisitos\n\nO cliente deve concluir o pagamento em até 30 s.\n",
        encoding="utf-8",
    )
    run = execute_run(tmp_path, project_locale="pt-BR", output_language="pt-BR")
    assert run.status == "AWAITING_AGENT"
    assert run.reasoning_request is not None
    assert run.reasoning_result is not None
    assert run.reasoning_result.status == "NOT_REQUESTED"
    assert run.scope.authority_assigned is False
    assert (Path(run.workspace) / "agent-request.json").is_file()
    assert (tmp_path / ".qe" / "report.html").is_file()
    assert (tmp_path / ".qe" / "report.md").is_file()
    assert yaml.safe_load((tmp_path / ".qe" / "test-cases.yaml").read_text(encoding="utf-8")) == []


def test_agent_response_remains_non_normative_and_creates_ptbr_question(tmp_path: Path) -> None:
    (tmp_path / "requisitos.md").write_text(
        "O cliente deve concluir o pagamento em até 30 s.", encoding="utf-8"
    )
    initial = execute_run(tmp_path, project_locale="pt-BR", output_language="pt-BR")
    assert initial.reasoning_request is not None
    excerpt_id = initial.reasoning_request.excerpts[0].id
    response = ProviderResponse(
        status="COMPLETE",
        proposals=[
            ProviderProposal(
                candidate_type="requirement",
                statement="O cliente deve concluir o pagamento em até 30 s.",
                source_excerpt_ids=[excerpt_id],
                interpretation="inferred",
                confidence=0.9,
            )
        ],
    )
    completed = execute_run(
        tmp_path,
        agent_response=response,
        project_locale="pt-BR",
        output_language="pt-BR",
    )
    assert completed.candidates is not None
    assert completed.candidates.candidates[0].inferred is True
    assert completed.normalization is not None
    assert completed.normalization.status == "REJECTED"
    assert completed.clarifications is not None
    assert completed.clarifications.questions[0].question.startswith("Como")
    assert completed.clarifications.answers_fabricated is False


def test_run_rejects_unknown_agent_evidence(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("The service must respond.", encoding="utf-8")
    response = ProviderResponse(
        status="COMPLETE",
        proposals=[
            ProviderProposal(
                candidate_type="requirement",
                statement="Invented",
                source_excerpt_ids=["unknown"],
            )
        ],
    )
    try:
        execute_run(tmp_path, agent_response=response)
    except ValueError as error:
        assert "unknown excerpt ids" in str(error)
    else:
        raise AssertionError("unknown agent evidence must be rejected")


def test_doctor_and_run_cli_expose_secondary_product_path(tmp_path: Path, capsys) -> None:
    assert main(["doctor"]) == 0
    doctor = json.loads(capsys.readouterr().out)
    assert doctor["primary_experience"] == "Agent Skill + AI agent"
    (tmp_path / "requirements.md").write_text("The system must respond.", encoding="utf-8")
    assert main(["run", str(tmp_path), "--semantic-mode", "deterministic-only"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["command"] == "run"
    assert result["external_writes"] is False
