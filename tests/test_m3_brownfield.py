from qe_skill.m2 import analyze_project
from qe_skill.m3 import generate_m3

from .helpers import representative
from .test_m2 import existing


def test_brownfield_keeps_history_and_emits_reviewable_diff() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    historical = existing("legacy", cleanup=[])
    model.nodes.append(historical)
    before = historical.model_dump(mode="json")
    report = generate_m3(model, analyze_project(model))
    revision = next(item for item in report.revisions if item.original_test.id == "legacy")
    assert revision.action == "IMPROVE"
    assert revision.field_diffs
    assert revision.historical_asset_mutated is False
    assert historical.model_dump(mode="json") == before


def test_brownfield_semantic_defect_proposes_revision_not_mutation() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    historical = existing("ambiguous", quality_flags=["AMBIGUOUS_ACTION"])
    model.nodes.append(historical)
    original = historical.original_text
    report = generate_m3(model, analyze_project(model))
    revision = next(item for item in report.revisions if item.original_test.id == "ambiguous")
    assert revision.action == "REVISE"
    assert revision.step_diffs
    assert historical.original_text == original
