import pytest

from qe_skill import domain as d
from qe_skill.m2 import (
    AnalysisConfig,
    analyze_project,
    deterministic_pairwise,
    validate_analysis_report,
)
from tests.helpers import reference, representative


def historical(identifier: str) -> d.HistoricalIdentity:
    return d.HistoricalIdentity(
        external_id=identifier,
        source_project="synthetic-history",
        source_snapshot="old",
        version="1",
        history_locators=[f"synthetic://{identifier}"],
        content_hash=(identifier[0] if identifier[0] in "abcdef" else "e") * 64,
    )


def existing(identifier: str, **changes: object) -> d.ExistingTest:
    values: dict[str, object] = {
        "id": identifier,
        "project_id": "synthetic",
        "snapshot_id": "v1",
        "name": identifier,
        "claims": [reference("claim")],
        "historical": historical(identifier),
        "original_text": "Synthetic historical test text.",
        "classification": "UNKNOWN",
        "objective": "Retain a synthetic record",
        "requirement_ids": [reference("requirement")],
        "criterion_ids": [reference("atom")],
        "actor_id": reference("actor"),
        "state_ids": [reference("state-1")],
        "channel_ids": [reference("api")],
        "risk_ids": [reference("risk")],
        "oracle_ids": [reference("oracle")],
        "path_ids": [reference("path")],
        "layer": "manual-system",
        "data_partition": "valid",
        "preconditions": ["Prepared synthetic state"],
        "actions": ["Perform the explicit action"],
        "expected_results": ["The synthetic record is retained."],
        "cleanup": ["Discard isolated data"],
        "environment": "synthetic",
        "parameterized_data": True,
    }
    values.update(changes)
    return d.ExistingTest.model_validate(values)


def finding_for(report, identifier: str):
    return next(item for item in report.findings if item.asset and item.asset.id == identifier)


def test_greenfield_builds_scenario_universe_without_historical_defects() -> None:
    model = representative()
    report = analyze_project(model)
    assert report.mode == "GREENFIELD"
    assert report.status == "COMPLETE"
    assert not any(item.asset and item.asset.id.startswith("existing") for item in report.findings)
    assert {item.technique for item in report.scenarios} >= {
        "PAIRWISE",
        "STATE_TRANSITION",
        "RISK_PACK",
    }
    risk_scenario = next(item for item in report.scenarios if item.origin == "RISK")
    assert risk_scenario.oracle is None and risk_scenario.readiness == "EXPLORATORY"
    assert validate_analysis_report(report, model).valid


def test_compound_requirement_without_explicit_atoms_is_not_silently_split() -> None:
    model = representative()
    model.nodes = [
        node for node in model.nodes if not isinstance(node, d.AtomicCriterion | d.GeneratedTest)
    ]
    model.tests.test_cases = []
    report = analyze_project(model)
    assert report.status == "PARTIAL"
    assert report.atomicity[0].status == "NO_EXPLICIT_ATOMS"
    assert report.atomicity[0].review_required
    assert report.coverage.denominator_reliable is False
    assert any(item.kind == "REQUIREMENT_NOT_ATOMIZED" for item in report.findings)


def test_nominal_and_atomic_behavioral_coverage_are_distinct() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.extend(
        [
            existing("existing-valid"),
            existing(
                "existing-nominal",
                criterion_ids=[],
            ),
        ]
    )
    report = analyze_project(model)
    assert report.coverage.nominal_linked_requirements == 1
    assert report.coverage.behaviorally_covered_atoms == 1
    assert report.coverage.atoms[0].state == "BEHAVIORALLY_COVERED"
    assert finding_for(report, "existing-valid").classification == "VALID_AS_IS"
    assert finding_for(report, "existing-nominal").classification == "PARTIAL_COVERAGE"


def test_exact_duplicate_uses_behavioral_signature_and_preserves_variants() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.extend(
        [
            existing("duplicate-a"),
            existing("duplicate-b"),
            existing("intentional", intentional_regression=True),
            existing("different-risk", risk_ids=[]),
        ]
    )
    report = analyze_project(model)
    assert finding_for(report, "duplicate-a").classification == "VALID_AS_IS"
    assert finding_for(report, "duplicate-b").classification == "DUPLICATE_REDUNDANT"
    assert finding_for(report, "intentional").classification == "DUPLICATE_INTENTIONAL"
    assert finding_for(report, "different-risk").classification == "VALID_AS_IS"
    assert all(node in model.nodes for node in model.nodes)


@pytest.mark.parametrize(
    ("identifier", "changes", "classification"),
    [
        ("untraceable", {"requirement_ids": [], "criterion_ids": []}, "UNTRACEABLE"),
        ("nonexec", {"actions": [], "path_ids": []}, "NON_EXECUTABLE"),
        ("ambiguous", {"quality_flags": ["AMBIGUOUS_ACTION"]}, "AMBIGUOUS"),
        ("unsupported", {"oracle_ids": []}, "AMBIGUOUS"),
        ("improve", {"cleanup": []}, "VALID_WITH_IMPROVEMENT"),
    ],
)
def test_existing_test_quality_classifications(
    identifier: str, changes: dict[str, object], classification: str
) -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.append(existing(identifier, **changes))
    report = analyze_project(model)
    assert finding_for(report, identifier).classification == classification
    assert model.nodes[-1].classification == "UNKNOWN"


def test_oracle_support_grouping_and_implementation_origin_stay_explicit() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.append(existing("grouped", quality_flags=["GROUPED_ORACLES"]))
    grouped = analyze_project(model)
    assert grouped.oracle_findings[0].status == "SUPPORTED_BUT_GROUPED"
    assert "SPLIT_GROUPED_ORACLE" in {item.kind for item in grouped.proposals}

    model.oracles[0].origin = "IMPLEMENTATION"
    model.oracles[0].usage = "characterization"
    model.oracles[0].normative = False
    model.claims[0].origin = "IMPLEMENTATION"
    model.ledger.sources[0].authority_class = "IMPLEMENTATION"
    implementation = analyze_project(model)
    assert implementation.oracle_findings[0].status == "IMPLEMENTATION_DERIVED_ONLY"


@pytest.mark.parametrize(
    ("lifecycle", "classification"),
    [("superseded", "STALE"), ("deprecated", "OBSOLETE_CANDIDATE")],
)
def test_stale_and_obsolete_are_non_destructive_review_states(
    lifecycle: str, classification: str
) -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    requirement = next(node for node in model.nodes if isinstance(node, d.Requirement))
    requirement.lifecycle = lifecycle  # type: ignore[assignment]
    model.nodes.append(existing(f"asset-{lifecycle}"))
    report = analyze_project(model)
    assert finding_for(report, f"asset-{lifecycle}").classification == classification
    assert report.historical_assets_mutated is False


def test_explicit_conflicting_expected_result_is_not_normalized() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.append(existing("conflicting", quality_flags=["CONFLICTING_EXPECTED_RESULT"]))
    before = model.nodes[-1].original_text
    report = analyze_project(model)
    assert finding_for(report, "conflicting").classification == "CONFLICTING"
    assert model.nodes[-1].original_text == before


def test_incomplete_source_blocks_audit_certainty_and_coverage() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.append(existing("blocked"))
    model.ledger.manifest.completeness = "PARTIAL"
    model.ledger.sources[0].study_status = "BLOCKED"
    model.ledger.sources[0].read_integrity = "FAILED"
    model.ledger.sources[0].reason = "Synthetic unavailable source"
    report = analyze_project(model)
    assert report.status in {"PARTIAL", "INVALID"}
    assert not report.coverage.denominator_reliable
    assert report.coverage.atoms[0].state == "BLOCKED_UNKNOWN"
    assert finding_for(report, "blocked").classification == "BLOCKED_BY_SOURCE"


def test_clone_revalidates_destination_and_never_inherits_old_oracle() -> None:
    model = representative()
    model.ledger.manifest.mode = "CLONE_REUSE"
    model.nodes.extend(
        [
            existing("clone-reusable"),
            existing("clone-old-oracle", oracle_ids=[]),
        ]
    )
    report = analyze_project(model)
    assert report.clone_classifications == {
        "clone-old-oracle": "UNKNOWN",
        "clone-reusable": "REUSABLE",
    }
    assert (
        next(item for item in report.oracle_findings if item.test.id == "clone-old-oracle").status
        == "UNSUPPORTED"
    )


def test_boundary_partition_pairwise_and_selection_are_deterministic_and_bounded() -> None:
    model = representative()
    constraint = next(node for node in model.nodes if isinstance(node, d.Constraint))
    constraint.value_type = "length"
    constraint.minimum = 1
    constraint.maximum = 3
    constraint.partitions = ["valid", "invalid-empty"]
    atom = next(node for node in model.nodes if isinstance(node, d.AtomicCriterion))
    atom.boundaries = [reference("constraint")]
    first = analyze_project(model, AnalysisConfig(max_scenarios=2, max_pairwise_combinations=2))
    second = analyze_project(model, AnalysisConfig(max_scenarios=2, max_pairwise_combinations=2))
    assert first.model_dump() == second.model_dump()
    assert {item.technique for item in first.scenarios} >= {
        "BOUNDARY_VALUE",
        "EQUIVALENCE_PARTITION",
        "PAIRWISE",
    }
    assert sum(item.disposition == "SELECTED" for item in first.dispositions) <= 2
    combinations = deterministic_pairwise(
        {"actor": ["a", "b"], "state": ["x", "y"], "channel": ["api", "ui"]}, 4
    )
    assert combinations == deterministic_pairwise(
        {"channel": ["ui", "api"], "state": ["y", "x"], "actor": ["b", "a"]}, 4
    )
    assert len(combinations) <= 4


def test_explicit_decision_rule_produces_no_invented_outcome_oracle() -> None:
    model = representative()
    model.nodes.append(
        d.DecisionRule(
            id="decision",
            project_id="synthetic",
            snapshot_id="v1",
            name="Explicit synthetic decision",
            claims=[reference("claim")],
            conditions=[reference("constraint")],
            outcome=reference("claim"),
            action=reference("action"),
        )
    )
    report = analyze_project(model)
    scenario = next(item for item in report.scenarios if item.technique == "DECISION_TABLE")
    assert scenario.stimulus and scenario.stimulus.id == "action"
    assert scenario.oracle is None


def test_history_is_operational_evidence_and_input_is_immutable() -> None:
    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    test = existing("history")
    model.nodes.append(test)
    for index, outcome in enumerate(("PASS", "FAIL", "FAIL")):
        model.nodes.append(
            d.ExistingResult(
                id=f"history-result-{index}",
                project_id="synthetic",
                snapshot_id="v1",
                name=f"result {index}",
                claims=[reference("claim")],
                historical=historical(f"result-{index}"),
                test=reference("history"),
                outcome=outcome,
                original_text="Preserved historical result.",
            )
        )
    before = model.model_dump(mode="json")
    report = analyze_project(model)
    assert model.model_dump(mode="json") == before
    assert report.history_summary["history"] == {"FAIL": 2, "PASS": 1}
    assert any(item.kind == "REPEATED_FAIL" for item in report.findings)
    assert all(not item.external_operations for item in report.proposals)


def test_report_binding_rejects_mutation_and_foreign_scope() -> None:
    model = representative()
    report = analyze_project(model)
    model.claims[0].statement = "Mutated after analysis."
    assert "M2_STALE_INPUT" in {
        item.code for item in validate_analysis_report(report, model).issues
    }
    report.project_id = "foreign"
    assert "SCOPE_NAMESPACE" in {
        item.code for item in validate_analysis_report(report, model).issues
    }


def test_regression_mode_is_explicitly_out_of_scope() -> None:
    model = representative()
    model.ledger.manifest.mode = "REGRESSION_AUDIT"
    with pytest.raises(ValueError, match="outside M2"):
        analyze_project(model)
