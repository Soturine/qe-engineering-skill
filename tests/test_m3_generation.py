from qe_skill.m2 import analyze_project
from qe_skill.m3 import AuthoringConfig, generate_m3, validate_generation_report

from .helpers import representative


def test_greenfield_selected_scenarios_generate_deterministic_proposals() -> None:
    model = representative()
    analysis = analyze_project(model)
    first = generate_m3(model, analysis)
    second = generate_m3(model, analysis)
    assert first == second
    assert first.cases
    assert all(case.proposal_only for case in first.cases)
    assert any(edge.relation == "SCENARIO_TO_CASE" for edge in first.traceability)
    assert validate_generation_report(first, model, analysis).valid


def test_missing_authoring_context_is_exposed_not_invented() -> None:
    model = representative()
    report = generate_m3(model, analyze_project(model))
    blocked = [case for case in report.cases if case.readiness == "BLOCKED_SOURCE"]
    assert blocked
    assert any("Environment evidence" in note for note in blocked[0].blocking_notes)
    assert blocked[0].materialized_test is None


def test_generation_rejects_stale_m2_input() -> None:
    model = representative()
    analysis = analyze_project(model)
    model.claims[0].statement = "The changed synthetic statement is retained."
    try:
        generate_m3(model, analysis, AuthoringConfig())
    except ValueError as error:
        assert "same snapshot" in str(error)
    else:
        raise AssertionError("stale M2 input was accepted")


def test_complete_supported_context_materializes_strict_ready_case() -> None:
    model = representative()
    analysis = analyze_project(model)
    config = AuthoringConfig(
        environment_claim={"id": "instruction-2", "project_id": "synthetic", "snapshot_id": "v1"},
        cleanup_claim={"id": "instruction-6", "project_id": "synthetic", "snapshot_id": "v1"},
        isolation_claim={"id": "instruction-7", "project_id": "synthetic", "snapshot_id": "v1"},
        build="synthetic-1",
        profile="synthetic role",
    )
    generated = generate_m3(model, analysis, config)
    ready = [case for case in generated.cases if case.readiness == "READY"]
    assert ready and ready[0].materialized_test is not None
    assert validate_generation_report(generated, model, analysis).valid
