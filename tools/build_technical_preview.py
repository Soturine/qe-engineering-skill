"""Build the repository's synthetic PT-BR Technical Preview without network access."""

from __future__ import annotations

import json
from pathlib import Path

from qe_skill.adjudication import RelationInput, build_relation_graph
from qe_skill.m2 import analyze_project
from qe_skill.m3 import generate_m3, validate_generation_report
from qe_skill.m3_render import ReportTheme, render_html, render_markdown
from qe_skill.normalization import normalize_candidate_set
from qe_skill.review import ReviewContext
from tests.helpers import representative
from tests.normalization_helpers import prepared, simple_meaning

OUTPUT = Path(__file__).parents[1] / "examples" / "technical-preview" / "output"


def _ptbr_model():
    model = representative()
    model.ledger.manifest.project_locale = "pt-BR"
    model.ledger.manifest.output_language = "pt-BR"
    model.ledger.manifest.scope_description = "Contrato sintético de pedidos"
    model.ledger.sources[0].source_language = "pt-BR"
    model.ledger.sources[0].locator = "demo://requisitos-pedidos"
    replacements = {
        "The synthetic record is retained.": "O pedido deve permanecer inalterado.",
        "Open the synthetic record endpoint with the prepared identifier.": (
            "Consulte GET /orders/{order_id} usando o order_id preparado."
        ),
        "Use the isolated synthetic environment.": "Use o ambiente sintético isolado.",
        "Prepare one synthetic record in the intermediate state.": (
            "Prepare um pedido sintético no estado PENDING."
        ),
        "Use the prepared record identifier.": "Use o order_id do pedido preparado.",
        "Record the identifier during preparation.": "Registre o order_id durante a preparação.",
        "Discard the isolated synthetic environment after the test.": (
            "Descarte o ambiente sintético isolado após o teste."
        ),
        "Use a fresh isolated synthetic environment for every run.": (
            "Use um ambiente sintético novo e isolado em cada execução."
        ),
    }
    for claim in model.claims:
        claim.statement = replacements.get(claim.statement, claim.statement)
    for node in model.nodes:
        if node.kind == "verified_path":
            for step in node.steps:
                step.instruction = replacements.get(step.instruction, step.instruction)
    model.oracles[0].statement = replacements[model.oracles[0].statement]
    case = model.tests.test_cases[0]
    case.title = "Manter pedido faturado inalterado"
    case.objective = "Verificar que o pedido faturado não é alterado."
    case.environment.text = replacements[case.environment.text]
    case.preconditions[0].text = replacements[case.preconditions[0].text]
    case.data[0].properties.text = replacements[case.data[0].properties.text]
    case.data[0].preparation.text = replacements[case.data[0].preparation.text]
    case.steps[0].action.text = replacements[case.steps[0].action.text]
    case.steps[0].expected_result = model.oracles[0].statement
    case.steps[0].evidence_expectation = "Registre o estado observado e o order_id."
    case.pass_rule = "Todos os passos obrigatórios satisfazem seus oráculos."
    case.fail_rule = "Um passo obrigatório contradiz seu oráculo; identifique o passo."
    case.blocked_rule = "A preparação ou observação obrigatória não pode ser concluída."
    case.cleanup.text = replacements[case.cleanup.text]
    case.isolation.text = replacements[case.isolation.text]
    return model


def _conflicting_inputs() -> list[RelationInput]:
    inputs: list[RelationInput] = []
    for text, modality, polarity, source, authority in (
        (
            "O cliente pode cancelar o pedido antes do faturamento.",
            "MAY",
            "POSITIVE",
            "prd",
            "CONTRACT",
        ),
        (
            "O cliente não pode cancelar o pedido após pagamento confirmado.",
            "MUST_NOT",
            "NEGATIVE",
            "adr",
            "TECHNICAL_CONTRACT",
        ),
    ):
        model, request, result, candidates = prepared(
            text,
            simple_meaning(
                actor_label="customer",
                actor_surface="cliente",
                capability_label="cancel_order",
                capability_surface="cancelar o pedido",
                modality=modality,
                polarity=polarity,
            ),
            source_id=source,
            source_language="pt-BR",
            authority_class=authority,
        )
        inputs.append(
            RelationInput(
                normalization=normalize_candidate_set(candidates, request, result, model.ledger),
                candidates=candidates,
                request=request,
                result=result,
                ledger=model.ledger,
            )
        )
    return inputs


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    model = _ptbr_model()
    analysis = analyze_project(model)
    report = generate_m3(model, analysis)
    validation = validate_generation_report(report, model, analysis)
    if not validation.valid:
        raise RuntimeError("The generated Technical Preview did not pass deterministic validation.")
    inputs = _conflicting_inputs()
    context = ReviewContext(
        project_model=model,
        analysis=analysis,
        semantic_inputs=inputs,
        relations=build_relation_graph(inputs),
    )
    context.validate_for(report)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    write_json(OUTPUT / "project-model.json", model.model_dump(mode="json"))
    write_json(OUTPUT / "m2-analysis-report.json", analysis.model_dump(mode="json"))
    write_json(OUTPUT / "m3-generation-report.json", report.model_dump(mode="json"))
    write_json(OUTPUT / "review-context.json", context.model_dump(mode="json"))
    (OUTPUT / "test-plan.md").write_text(
        render_markdown(report, ReportTheme(output_language="pt-BR")), encoding="utf-8"
    )
    (OUTPUT / "test-plan.html").write_text(
        render_html(
            report,
            ReportTheme(project_name="Plano de Testes — Pedidos", output_language="pt-BR"),
            context=context,
        ),
        encoding="utf-8",
    )
    print(OUTPUT / "test-plan.html")


if __name__ == "__main__":
    main()
