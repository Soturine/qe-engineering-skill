from qe_skill.m2 import analyze_project
from qe_skill.m3 import (
    DraftManualStep,
    DraftSupportedText,
    DraftTestData,
    GeneratedCaseProposal,
    generate_m3,
    propose_parameters,
    propose_shared_steps,
)

from .helpers import ref, reference, representative
from .test_m3_contracts import unresolved_case


def proposal(identifier: str) -> GeneratedCaseProposal:
    payload = unresolved_case()
    payload.update(ref(identifier))
    payload["preconditions"] = [{"text": "Prepare the synthetic record.", "claims": [ref("claim")]}]
    return GeneratedCaseProposal.model_validate(payload)


def test_repeated_stable_preparation_becomes_shared_step_candidate() -> None:
    candidates = propose_shared_steps([proposal("case-a"), proposal("case-b")])
    assert len(candidates) == 1
    assert len(candidates[0].used_by) == 2


def test_one_off_preparation_and_core_action_are_not_shared() -> None:
    assert propose_shared_steps([proposal("case-a")]) == []


def test_parameter_candidate_requires_evidence_and_never_invents_values() -> None:
    case = proposal("case-a")
    case.data = [
        DraftTestData(
            name="record identifier",
            properties=DraftSupportedText(
                text="Use the prepared identifier.", claims=[case.primary_provenance[0]]
            ),
            preparation=DraftSupportedText(
                text="Record it during setup.", claims=[case.primary_provenance[0]]
            ),
        )
    ]
    candidates = propose_parameters([case])
    assert len(candidates) == 1
    assert candidates[0].candidate_values == []


def test_repeated_verified_setup_prefix_becomes_shared_step() -> None:
    first, second = proposal("case-a"), proposal("case-b")
    for case in (first, second):
        case.preconditions = []
        case.steps = [
            DraftManualStep(
                number=1,
                phase="NAVIGATION",
                action=DraftSupportedText(text="Open records.", claims=[ref("claim")]),
                path=ref("path"),
            ),
            DraftManualStep(
                number=2,
                phase="VALIDATION",
                action=DraftSupportedText(text="Observe record.", claims=[ref("claim")]),
                oracle=ref("oracle"),
            ),
        ]
    candidates = propose_shared_steps([first, second])
    assert len(candidates) == 1
    assert candidates[0].steps[0].oracle is None


def test_explicit_partition_and_values_are_preserved() -> None:
    case = proposal("case-a")
    case.data = [
        DraftTestData(
            name="valid quantity",
            properties=DraftSupportedText(text="Explicit valid partition.", claims=[ref("claim")]),
            preparation=DraftSupportedText(unresolved_reasons=["Operator supplies value."]),
            partition="valid",
            constraints=[ref("constraint")],
            candidate_values=["1", "100"],
        )
    ]
    candidate = propose_parameters([case])[0]
    assert candidate.partitions == ["valid"]
    assert candidate.candidate_values == ["1", "100"]
    assert candidate.constraints == [reference for reference in case.data[0].constraints]


def test_m2_partition_produces_linked_parameter_candidate() -> None:
    model = representative()
    constraint = next(node for node in model.nodes if node.id == "constraint")
    atom = next(node for node in model.nodes if node.id == "atom")
    assert hasattr(constraint, "partitions") and hasattr(atom, "boundaries")
    constraint.partitions = ["valid identifier"]
    atom.boundaries = [reference("constraint")]
    report = generate_m3(model, analyze_project(model))
    candidate = next(item for item in report.parameters if item.name == "valid identifier")
    assert candidate.partitions == ["valid identifier"]
    assert candidate.constraints == [reference("constraint")]
    linked_case = next(
        item
        for item in report.cases
        if candidate.id in {ref.id for ref in item.parameter_candidates}
    )
    assert linked_case.data[0].parameter_candidate is not None
