import pytest
from pydantic import ValidationError

from qe_skill.m3 import GeneratedCaseProposal, M3GenerationReport

from .helpers import ref


def binding() -> dict[str, object]:
    return {
        "project_model_hash": "a" * 64,
        "m2_analysis_hash": "b" * 64,
        "generator_version": "0.3.0",
        "configuration_hash": "c" * 64,
    }


def unresolved_case() -> dict[str, object]:
    return {
        **ref("case-proposal"),
        "action": "NEW",
        "title": "Review synthetic retention",
        "objective": {
            "claims": [ref("claim")],
            "unresolved_reasons": ["Executable action is not established."],
        },
        "origin": "CONTRACT",
        "primary_provenance": [ref("claim")],
        "requirements": [],
        "criteria": [],
        "risks": [],
        "scenarios": [ref("scenario")],
        "priority_rationale": "Selected by the upstream scenario analysis.",
        "environment": {"claims": [], "unresolved_reasons": ["Environment is unknown."]},
        "blocked_rule": "Required source evidence is unavailable.",
        "cleanup": {"claims": [], "unresolved_reasons": ["Cleanup is unknown."]},
        "isolation": {"claims": [], "unresolved_reasons": ["Isolation is unknown."]},
        "readiness": "BLOCKED_SOURCE",
        "blocking_notes": ["Source evidence does not define an executable procedure."],
        "review_status": "REVIEW_REQUIRED",
        "rationale": "Retain the scenario without inventing missing procedure details.",
    }


def test_unresolved_non_ready_draft_is_representable() -> None:
    proposal = GeneratedCaseProposal.model_validate(unresolved_case())
    assert proposal.materialized_test is None
    assert proposal.objective.text is None
    assert proposal.readiness == "BLOCKED_SOURCE"


def test_ready_draft_requires_materialized_strict_test_case() -> None:
    payload = unresolved_case()
    payload["readiness"] = "READY"
    payload["blocking_notes"] = []
    with pytest.raises(ValidationError, match="materialized TestCase"):
        GeneratedCaseProposal.model_validate(payload)


def test_contracts_forbid_unknown_fields() -> None:
    payload = unresolved_case()
    payload["invented"] = True
    with pytest.raises(ValidationError):
        GeneratedCaseProposal.model_validate(payload)


def test_cross_snapshot_reference_is_rejected() -> None:
    payload = unresolved_case()
    payload["scenarios"] = [{"id": "scenario", "project_id": "synthetic", "snapshot_id": "v2"}]
    with pytest.raises(ValidationError, match="cross-scope"):
        GeneratedCaseProposal.model_validate(payload)


def test_report_rejects_manifest_binding_mismatch() -> None:
    input_binding = binding()
    other_binding = {**input_binding, "m2_analysis_hash": "d" * 64}
    payload = {
        **ref("report"),
        "mode": "GREENFIELD",
        "status": "PARTIAL",
        "input_binding": input_binding,
        "cases": [unresolved_case()],
        "test_model": {**ref("generated-tests"), "test_cases": [], "proposal_only": True},
        "revisions": [],
        "shared_steps": [],
        "parameters": [],
        "traceability": [],
        "materialized_oracles": [],
        "manifest": {
            **ref("manifest"),
            "mode": "GREENFIELD",
            "input_binding": other_binding,
            "configuration": {},
            "artifact_refs": [ref("case-proposal")],
            "created_at": "2026-01-01T00:00:00Z",
            "tool_version": "0.3.0",
        },
        "limitations": ["Executable evidence remains incomplete."],
    }
    with pytest.raises(ValidationError, match="binding differs"):
        M3GenerationReport.model_validate(payload)
