import json

import yaml

from qe_skill import domain as d
from qe_skill.adjudication import RelationInput, build_relation_graph
from qe_skill.m2 import analyze_project
from qe_skill.m3 import (
    DraftSupportedText,
    DraftTestData,
    generate_m3,
    propose_parameters,
    propose_shared_steps,
)
from qe_skill.m3_render import (
    ReportTheme,
    render_canonical,
    render_html,
    render_json,
    render_markdown,
    render_yaml,
)
from qe_skill.normalization import normalize_candidate_set
from qe_skill.review import ReviewContext

from .helpers import representative
from .normalization_helpers import prepared, simple_meaning


def test_renderers_preserve_canonical_core_facts_deterministically() -> None:
    model = representative()
    report = generate_m3(model, analyze_project(model))
    json_text = render_json(report)
    yaml_text = render_yaml(report)
    markdown = render_markdown(report)
    page = render_html(report)
    assert json.loads(json_text)["snapshot_id"] == "v1"
    assert yaml.safe_load(yaml_text)["snapshot_id"] == "v1"
    for rendered in (markdown, page):
        assert "GREENFIELD" in rendered
        assert "v1" in rendered
        assert report.cases[0].readiness in rendered
    assert render_json(report) == json_text


def test_html_escapes_untrusted_project_content() -> None:
    model = representative()
    report = generate_m3(model, analyze_project(model))
    report.cases[0].title = "<script>alert('x')</script>"
    page = render_html(report)
    assert "<script>" not in page
    assert "&lt;script&gt;" in page


def test_optional_empty_sections_are_omitted() -> None:
    _, _, report = _report()
    page = render_html(report)
    assert 'id="shared"' not in page
    assert 'id="parameters"' not in page
    assert 'id="changes"' not in page


def test_additive_future_field_is_ignored_but_major_version_fails() -> None:
    _, _, report = _report()
    payload = report.model_dump(mode="json")
    payload["future_additive"] = {"safe": True}
    assert "Test Cases" in render_canonical(payload, "html")
    payload["schema_version"] = "2.0"
    try:
        render_canonical(payload, "html")
    except ValueError as error:
        assert "major version" in str(error)
    else:
        raise AssertionError("incompatible schema rendered")


def test_renderer_is_offline_and_theme_changes_presentation_only() -> None:
    _, _, report = _report()
    canonical = render_json(report)
    page = render_html(report, ReportTheme(project_name="Synthetic Review", accent="#123456"))
    assert "Synthetic Review" in page and "#123456" in page
    assert "http://" not in page and "https://" not in page
    assert render_json(report) == canonical


def test_ptbr_project_defaults_to_localized_review_without_translating_content() -> None:
    model, analysis, report = _report()
    model.ledger.manifest.project_locale = "pt-BR"
    model.ledger.manifest.output_language = "source"
    report = generate_m3(model, analyze_project(model))
    page = render_html(
        report, context=ReviewContext(project_model=model, analysis=analyze_project(model))
    )
    assert '<html lang="pt-BR">' in page
    for label in ("Plano de Testes", "Visão Geral", "Casos de Teste", "Resultado Esperado"):
        assert label in page
    assert "The synthetic record is retained." in page
    assert "access_token" not in page
    assert "https://" not in page and "http://" not in page
    assert "@media(max-width:700px)" in page and 'id="search"' in page
    assert "focus-visible" in page and 'aria-live="polite"' in page
    markdown = render_markdown(report, ReportTheme(output_language="pt-BR"))
    assert "# Plano de Testes" in markdown and "Revisar cenário" in markdown


def test_review_context_exposes_validated_evidence_and_h4_conflict() -> None:
    model, analysis, report = _report()
    inputs: list[RelationInput] = []
    for text, modality, source in (
        ("O cliente deve confirmar por SMS.", "MUST", "prd"),
        ("O cliente não pode confirmar por SMS.", "MUST_NOT", "adr"),
    ):
        semantic_model, request, result, candidates = prepared(
            text,
            simple_meaning(
                actor_label="customer",
                actor_surface="cliente",
                capability_label="confirm_sms",
                capability_surface="confirmar por SMS",
                modality=modality,
                polarity="NEGATIVE" if modality == "MUST_NOT" else "POSITIVE",
            ),
            source_id=source,
            source_language="pt-BR",
        )
        inputs.append(
            RelationInput(
                normalization=normalize_candidate_set(
                    candidates, request, result, semantic_model.ledger
                ),
                candidates=candidates,
                request=request,
                result=result,
                ledger=semantic_model.ledger,
            )
        )
    graph = build_relation_graph(inputs)
    context = ReviewContext(
        project_model=model, analysis=analysis, semantic_inputs=inputs, relations=graph
    )
    page = render_html(report, ReportTheme(output_language="pt-BR"), context=context)
    assert "Conflitos" in page and "Conflitante" in page
    assert "Revisão humana necessária" in page
    assert "O cliente deve confirmar por SMS." in page
    assert "sem vencedor normativo" in page
    assert f'href="#case-{report.cases[0].id}"' in page


def test_brownfield_original_and_proposed_are_visible() -> None:
    from .test_m2 import existing

    model = representative()
    model.ledger.manifest.mode = "BROWNFIELD"
    model.nodes.append(existing("legacy", actions=[]))
    report = generate_m3(model, analyze_project(model))
    page = render_html(report)
    assert "Original" in page and "Proposed" in page
    assert "Historical asset modified? NO" in page


def test_shared_step_and_parameter_sections_link_to_using_cases() -> None:
    from .helpers import ref
    from .test_m3_candidates import proposal

    _, _, report = _report()
    first, second = proposal("render-case-a"), proposal("render-case-b")
    first.data = [
        DraftTestData(
            name="record identifier",
            properties=DraftSupportedText(
                text="Use the prepared identifier.", claims=[ref("claim")]
            ),
            preparation=DraftSupportedText(text="Record it during setup.", claims=[ref("claim")]),
        )
    ]
    report.cases = [first, second]
    report.shared_steps = propose_shared_steps(report.cases)
    report.parameters = propose_parameters(report.cases)
    first.shared_step_candidates = [
        d.Ref(
            id=report.shared_steps[0].id,
            project_id=first.project_id,
            snapshot_id=first.snapshot_id,
        )
    ]
    first.parameter_candidates = [
        d.Ref(
            id=report.parameters[0].id,
            project_id=first.project_id,
            snapshot_id=first.snapshot_id,
        )
    ]

    page = render_html(report)
    assert f'id="shared-{report.shared_steps[0].id}"' in page
    assert f'href="#shared-{report.shared_steps[0].id}"' in page
    assert f'id="parameter-{report.parameters[0].id}"' in page
    assert f'href="#parameter-{report.parameters[0].id}"' in page
    assert "Used by:" in page


def _report():
    model = representative()
    analysis = analyze_project(model)
    return model, analysis, generate_m3(model, analysis)
