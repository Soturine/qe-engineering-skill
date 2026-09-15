import json

import yaml

from qe_skill import domain as d
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

from .helpers import representative


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
