from qe_skill import domain as d
from qe_skill.m2 import analyze_project
from qe_skill.m3 import AuthoringConfig, generate_m3, validate_generation_report

from .helpers import claim_copy, reference, representative


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


def test_verified_multistep_path_becomes_complete_ordered_procedure() -> None:
    model = representative()
    path = next(node for node in model.nodes if node.id == "path")
    assert hasattr(path, "steps")
    navigation = claim_copy(model, "navigate-claim")
    navigation.statement = "Open the synthetic records collection."
    action = claim_copy(model, "select-claim")
    action.statement = "Select the prepared synthetic record."
    model.claims.extend([navigation, action])
    path.steps = [
        {
            "instruction": navigation.statement,
            "claim": reference(navigation.id),
            "phase": "NAVIGATION",
        },
        {"instruction": action.statement, "claim": reference(action.id), "phase": "ACTION"},
    ]
    generated = generate_m3(model, analyze_project(model))
    case = next(item for item in generated.cases if item.origin == "CONTRACT")
    assert [step.number for step in case.steps] == [1, 2]
    assert [step.phase for step in case.steps] == ["NAVIGATION", "ACTION"]
    assert case.steps[0].oracle is None
    assert case.steps[1].oracle is not None


def test_partial_path_preserves_known_steps_without_fabricating_remainder() -> None:
    model = representative()
    model.tests.test_cases = []
    model.nodes = [node for node in model.nodes if not isinstance(node, d.GeneratedTest)]
    path = next(node for node in model.nodes if node.id == "path")
    assert hasattr(path, "verification_status")
    path.verification_status = "partial"
    generated = generate_m3(model, analyze_project(model))
    case = next(item for item in generated.cases if item.origin == "CONTRACT")
    assert len(case.steps) == 1
    assert case.readiness == "BLOCKED_SOURCE"
    assert any("no remainder was invented" in note for note in case.blocking_notes)


def test_high_risk_evidence_is_stronger_without_creating_an_oracle() -> None:
    low_model = representative()
    low = generate_m3(low_model, analyze_project(low_model))
    low_case = next(case for case in low.cases if case.origin == "RISK")

    high_model = representative()
    risk = next(node for node in high_model.nodes if isinstance(node, d.Risk))
    risk.severity = "high"
    high = generate_m3(high_model, analyze_project(high_model))
    high_case = next(case for case in high.cases if case.origin == "RISK")

    assert len(high_case.evidence_expectations) > len(low_case.evidence_expectations)
    assert any(
        "context sufficient to reproduce" in step.evidence_expectation for step in high_case.steps
    )
    assert high_case.review_status == "REVIEW_REQUIRED"
    assert high_case.readiness == "EXPLORATORY_ONLY"
    assert high_case.pass_rule is None and high_case.fail_rule is None
    assert high_case.steps[-1].oracle is None
    assert high.materialized_oracles == low.materialized_oracles


def test_generation_validator_rejects_dangling_refs_and_nonconsecutive_steps() -> None:
    model = representative()
    analysis = analyze_project(model)
    report = generate_m3(model, analysis)
    case = report.cases[0]
    case.scenarios = [reference("missing-scenario")]
    case.steps[0].number = 2
    issues = validate_generation_report(report, model, analysis)
    assert {issue.code for issue in issues.issues} >= {"M3_DANGLING_REF", "M3_STEP_SEQUENCE"}


def test_generation_validator_rejects_expected_result_oracle_mismatch() -> None:
    model = representative()
    analysis = analyze_project(model)
    report = generate_m3(model, analysis)
    case = next(item for item in report.cases if item.steps[-1].oracle is not None)
    case.steps[-1].expected_result = "A stronger unsupported result."
    assert "M3_ORACLE_MISMATCH" in {
        issue.code for issue in validate_generation_report(report, model, analysis).issues
    }
