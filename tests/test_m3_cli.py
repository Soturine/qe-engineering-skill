import json
from pathlib import Path

from qe_skill.cli import main
from qe_skill.m2 import analyze_project

from .helpers import representative


def write_inputs(root: Path) -> tuple[Path, Path]:
    model = representative()
    analysis = analyze_project(model)
    model_path = root / "project-model.json"
    analysis_path = root / "m2-analysis-report.json"
    model_path.write_text(json.dumps(model.model_dump(mode="json")), encoding="utf-8")
    analysis_path.write_text(json.dumps(analysis.model_dump(mode="json")), encoding="utf-8")
    return model_path, analysis_path


def test_generate_cli_writes_only_local_review_artifacts(tmp_path: Path) -> None:
    model_path, analysis_path = write_inputs(tmp_path)
    output = tmp_path / "m3-output"
    assert (
        main(
            [
                "generate",
                str(model_path),
                "--analysis",
                str(analysis_path),
                "--output-dir",
                str(output),
            ]
        )
        == 0
    )
    expected = {
        "m3-generation-report.json",
        "test-model.json",
        "test-model.yaml",
        "test-plan.md",
        "test-plan.html",
        "improvement-proposals.json",
        "improvement-report.md",
        "improvement-report.html",
        "shared-step-candidates.json",
        "parameter-candidates.json",
        "generation-traceability.json",
        "generation-manifest.json",
    }
    assert {path.name for path in output.iterdir()} == expected


def test_generate_cli_rejects_stale_analysis(tmp_path: Path) -> None:
    model_path, analysis_path = write_inputs(tmp_path)
    value = json.loads(model_path.read_text(encoding="utf-8"))
    value["claims"][0]["statement"] = "Changed after M2."
    model_path.write_text(json.dumps(value), encoding="utf-8")
    assert (
        main(
            [
                "generate",
                str(model_path),
                "--analysis",
                str(analysis_path),
                "--output-dir",
                str(tmp_path / "out"),
            ]
        )
        == 1
    )
