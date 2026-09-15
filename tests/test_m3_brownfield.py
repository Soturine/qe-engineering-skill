from qe_skill.m2 import analyze_project
from qe_skill.m3 import AuthoringConfig, generate_m3

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
    assert revision.original_hash
    assert revision.original_text == historical.original_text
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


def test_repairable_non_executable_asset_gets_complete_supported_revision() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    historical = existing("non-executable", actions=[], path_ids=[])
    model.nodes.append(historical)
    config = AuthoringConfig(
        environment_claim={"id": "instruction-2", "project_id": "synthetic", "snapshot_id": "v1"},
        cleanup_claim={"id": "instruction-6", "project_id": "synthetic", "snapshot_id": "v1"},
        isolation_claim={"id": "instruction-7", "project_id": "synthetic", "snapshot_id": "v1"},
        build="synthetic-1",
        profile="synthetic role",
    )
    report = generate_m3(model, analyze_project(model), config)
    revision = next(item for item in report.revisions if item.original_test.id == historical.id)
    proposed = next(
        item
        for item in report.cases
        if revision.proposed_case and item.id == revision.proposed_case.id
    )
    assert revision.action == "REVISE"
    assert revision.readiness == "READY"
    assert proposed.materialized_test is not None and proposed.materialized_test.steps
    assert historical.actions == []


def test_unsupported_untraceable_asset_stays_blocked_without_fake_replacement() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    historical = existing(
        "untraceable", requirement_ids=[], criterion_ids=[], oracle_ids=[], path_ids=[]
    )
    model.nodes.append(historical)
    report = generate_m3(model, analyze_project(model))
    revision = next(item for item in report.revisions if item.original_test.id == historical.id)
    assert revision.readiness == "BLOCKED_SOURCE"
    assert revision.proposed_case is None
    assert all(diff.after != "evidence-backed proposed value" for diff in revision.field_diffs)


def test_grouped_oracle_and_hard_coded_data_have_specific_review_diffs() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.append(
        existing("grouped-data", quality_flags=["GROUPED_ORACLES", "HARD_CODED_DATA"])
    )
    report = generate_m3(model, analyze_project(model))
    revision = next(item for item in report.revisions if item.original_test.id == "grouped-data")
    assert "test_data" in {diff.field for diff in revision.field_diffs}
    assert any("grouped" in diff.rationale for diff in revision.step_diffs)
