from pathlib import Path

from qe_skill import domain as d
from qe_skill.integrity import validate_project_model
from qe_skill.inventory import inventory_sources
from qe_skill.m2 import analyze_project
from qe_skill.m3 import generate_m3
from qe_skill.m3_render import render_html, render_json, render_markdown
from qe_skill.parsers import parse_entry
from tests.helpers import representative


def test_m0_ptbr_evidence_and_locale_round_trip_without_translation() -> None:
    model = representative()
    statement = "O usuário não pode excluir o registro sem aprovação."
    model.ledger.manifest.project_locale = "pt-BR"
    model.ledger.manifest.output_language = "pt-BR"
    model.ledger.sources[0].source_language = "pt-BR"
    model.claims[0].statement = statement
    model.oracles[0].statement = statement
    model.tests.test_cases[0].steps[0].expected_result = statement
    restored = d.ProjectModel.model_validate_json(model.model_dump_json())
    assert restored.claims[0].statement == statement
    assert restored.ledger.sources[0].source_language == "pt-BR"
    assert restored.ledger.manifest.project_locale == "pt-BR"
    assert restored.ledger.manifest.output_language == "pt-BR"
    assert validate_project_model(restored).valid


def test_m1_ptbr_mixed_markdown_preserves_unicode_spans_and_identifiers(tmp_path: Path) -> None:
    text = (
        "# Regra de autenticação\n\n"
        "O usuário realiza login pelo endpoint /auth/login e recebe access_token.\n"
    )
    path = tmp_path / "requisito.md"
    path.write_text(text, encoding="utf-8")
    inventory = inventory_sources(tmp_path, project_id="synthetic", snapshot_id="v1")
    parsed = parse_entry(tmp_path, inventory.entries[0])
    assert parsed.status == "PARSED"
    paragraph = next(item for item in parsed.extractions if item.kind == "paragraph")
    assert paragraph.text == (
        "O usuário realiza login pelo endpoint /auth/login e recebe access_token."
    )
    assert paragraph.span is not None and paragraph.span.line_start == 3


def test_m2_m3_keep_ptbr_oracle_and_render_human_content_in_project_language() -> None:
    model = representative()
    statement = "O pedido deve ser exibido com status APROVADO."
    model.ledger.manifest.project_locale = "pt-BR"
    model.ledger.manifest.output_language = "pt-BR"
    model.claims[0].statement = statement
    model.oracles[0].statement = statement
    model.tests.test_cases[0].steps[0].expected_result = statement
    analysis = analyze_project(model)
    report = generate_m3(model, analysis)
    assert report.cases
    assert any(step.expected_result == statement for case in report.cases for step in case.steps)
    for rendered in (render_json(report), render_markdown(report), render_html(report)):
        assert statement in rendered
