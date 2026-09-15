from qe_skill.m3 import (
    DraftSupportedText,
    DraftTestData,
    GeneratedCaseProposal,
    propose_parameters,
    propose_shared_steps,
)

from .helpers import ref
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
