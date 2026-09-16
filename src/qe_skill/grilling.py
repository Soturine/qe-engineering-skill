"""Bounded Scenario Grilling questions derived from deterministic M2 state."""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import Field

from qe_skill import domain as d
from qe_skill.localization import resolve_output_language
from qe_skill.m2 import M2AnalysisReport, ScenarioRecord

ProbeCategory = Literal[
    "MISSING_EVIDENCE",
    "AMBIGUOUS_RULE",
    "CONFLICT",
    "NO_NORMATIVE_ORACLE",
    "UNVERIFIED_PATH",
]


class ScenarioProbe(d.Artifact):
    scenario: d.Ref | None = None
    category: ProbeCategory
    question: d.Text
    rationale: d.Text
    sources: list[d.Ref] = Field(default_factory=list)
    blocking: bool
    status: Literal["OPEN"] = "OPEN"
    answer_fabricated: Literal[False] = False


class ScenarioGrill(d.Artifact):
    analysis: d.Ref
    probes: list[ScenarioProbe]
    project_locale: d.LanguageCode
    output_language: d.OutputLanguage
    bounded: Literal[True] = True
    external_writes: Literal[False] = False


_TEXT = {
    "en": {
        "MISSING_EVIDENCE": "Which source evidence is required to make this scenario executable?",
        "AMBIGUOUS_RULE": "Which reviewed rule should govern this scenario?",
        "CONFLICT": "Which cited authority resolves this conflict?",
        "NO_NORMATIVE_ORACLE": "Which approved source defines the observable expected result?",
        "UNVERIFIED_PATH": "Which verified path should the tester follow?",
    },
    "pt-BR": {
        "MISSING_EVIDENCE": "Qual evidência de fonte é necessária para tornar este cenário executável?",
        "AMBIGUOUS_RULE": "Qual regra revisada deve reger este cenário?",
        "CONFLICT": "Qual autoridade citada resolve este conflito?",
        "NO_NORMATIVE_ORACLE": "Qual fonte aprovada define o resultado esperado observável?",
        "UNVERIFIED_PATH": "Qual caminho verificado o testador deve seguir?",
    },
}


def _ref(record: d.Artifact) -> d.Ref:
    return d.Ref(id=record.id, project_id=record.project_id, snapshot_id=record.snapshot_id)


def _probe(
    report: M2AnalysisReport,
    scenario: ScenarioRecord | None,
    category: ProbeCategory,
    text: str,
    rationale: str,
    sources: list[d.Ref],
) -> ScenarioProbe:
    identity = json.dumps(
        [report.id, scenario.id if scenario else None, category, [item.id for item in sources]],
        separators=(",", ":"),
    )
    return ScenarioProbe(
        id=f"scenario-probe.{hashlib.sha256(identity.encode()).hexdigest()[:24]}",
        project_id=report.project_id,
        snapshot_id=report.snapshot_id,
        scenario=_ref(scenario) if scenario else None,
        category=category,
        question=text,
        rationale=rationale,
        sources=sources,
        blocking=category != "AMBIGUOUS_RULE" or (scenario is not None and scenario.origin != "EXPLORATORY"),
    )


def grill_scenarios(
    report: M2AnalysisReport,
    model: d.ProjectModel,
    *,
    max_probes: int = 100,
) -> ScenarioGrill:
    """Ask only questions justified by explicit report/model gaps; never infer answers."""

    if report.project_id != model.project_id or report.snapshot_id != model.snapshot_id:
        raise ValueError("scenario grill inputs cross project or snapshot scope")
    language = resolve_output_language(
        model.ledger.manifest.project_locale, model.ledger.manifest.output_language
    )
    catalog = _TEXT["pt-BR" if language == "pt-BR" else "en"]
    probes: list[ScenarioProbe] = []
    for scenario in report.scenarios:
        refs = [
            item
            for item in (scenario.source_requirement, scenario.source_atom, scenario.source_risk)
            if item is not None
        ]
        if scenario.oracle is None and scenario.origin not in {"RISK", "EXPLORATORY"}:
            probes.append(
                _probe(
                    report,
                    scenario,
                    "NO_NORMATIVE_ORACLE",
                    catalog["NO_NORMATIVE_ORACLE"],
                    "A normative scenario has no source-backed oracle.",
                    refs,
                )
            )
        if scenario.readiness == "BLOCKED":
            probes.append(
                _probe(
                    report,
                    scenario,
                    "MISSING_EVIDENCE",
                    catalog["MISSING_EVIDENCE"],
                    "M2 marked the scenario blocked.",
                    refs,
                )
            )
        elif scenario.readiness == "REVIEW_REQUIRED":
            probes.append(
                _probe(
                    report,
                    scenario,
                    "AMBIGUOUS_RULE",
                    catalog["AMBIGUOUS_RULE"],
                    "M2 requires review before this scenario can proceed.",
                    refs,
                )
            )
        if len(probes) >= max_probes:
            break
    for node in model.nodes:
        if isinstance(node, d.Conflict) and node.status in {"open", "unresolved"}:
            probes.append(
                _probe(
                    report,
                    None,
                    "CONFLICT",
                    catalog["CONFLICT"],
                    "An unresolved Project Model conflict can affect scenario authority.",
                    [_ref(node), *node.conflicting_claims],
                )
            )
        if len(probes) >= max_probes:
            break
    seed = json.dumps([report.id, [item.id for item in probes], language], separators=(",", ":"))
    return ScenarioGrill(
        id=f"scenario-grill.{hashlib.sha256(seed.encode()).hexdigest()[:24]}",
        project_id=report.project_id,
        snapshot_id=report.snapshot_id,
        analysis=_ref(report),
        probes=probes,
        project_locale=model.ledger.manifest.project_locale,
        output_language=language,
    )
