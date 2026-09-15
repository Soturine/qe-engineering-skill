from qe_skill.m3 import revalidate_clone_asset

from .helpers import representative
from .test_m2 import existing


def test_clone_revalidates_complete_destination_assumptions() -> None:
    model = representative()
    test = existing("clone")
    assert test.actor_id is not None
    test.source_assumption_refs = [test.actor_id, *test.path_ids, *test.oracle_ids]
    classification, _ = revalidate_clone_asset(test, model)
    assert classification == "REUSABLE"


def test_clone_missing_destination_assumption_is_unknown() -> None:
    model = representative()
    test = existing("clone")
    test.source_assumption_refs = [
        test.path_ids[0].model_copy(update={"id": "destination-path-missing"})
    ]
    classification, rationale = revalidate_clone_asset(test, model)
    assert classification == "UNKNOWN"
    assert "do not resolve" in rationale


def test_clone_never_inherits_non_normative_destination_oracle() -> None:
    model = representative()
    model.oracles[0].normative = False
    model.oracles[0].usage = "characterization"
    model.oracles[0].origin = "IMPLEMENTATION"
    model.claims[0].origin = "IMPLEMENTATION"
    model.ledger.sources[0].authority_class = "IMPLEMENTATION"
    classification, _ = revalidate_clone_asset(existing("clone"), model)
    assert classification == "CONFLICTING"
