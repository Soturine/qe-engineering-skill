from pathlib import Path

from tools import build_technical_preview


def test_ptbr_technical_preview_builds_offline_validated_review(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(build_technical_preview, "OUTPUT", tmp_path)
    build_technical_preview.main()
    expected = {
        "project-model.json",
        "m2-analysis-report.json",
        "m3-generation-report.json",
        "review-context.json",
        "test-plan.md",
        "test-plan.html",
    }
    assert {item.name for item in tmp_path.iterdir()} == expected
    page = (tmp_path / "test-plan.html").read_text(encoding="utf-8")
    assert '<html lang="pt-BR">' in page
    assert "Plano de Testes" in page and "Conflitos" in page
    assert "Revisão humana necessária" in page
    assert "GET /orders/{order_id}" in page and "PENDING" in page
    assert "http://" not in page and "https://" not in page
    assert "Nenhum cenário M2 selecionado" not in page
