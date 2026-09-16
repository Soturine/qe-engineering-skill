from qe_skill.grilling import grill_scenarios
from qe_skill.m2 import analyze_project
from tests.helpers import representative


def test_scenario_grilling_is_bounded_grounded_and_ptbr() -> None:
    model = representative()
    model.ledger.manifest.project_locale = "pt-BR"
    model.ledger.manifest.output_language = "pt-BR"
    analysis = analyze_project(model)
    grill = grill_scenarios(analysis, model, max_probes=3)
    assert 0 < len(grill.probes) <= 3
    assert grill.output_language == "pt-BR"
    assert {item.category for item in grill.probes} >= {
        "NO_NORMATIVE_ORACLE",
        "AMBIGUOUS_RULE",
    }
    assert all(item.status == "OPEN" and not item.answer_fabricated for item in grill.probes)
    assert all(item.sources for item in grill.probes)
