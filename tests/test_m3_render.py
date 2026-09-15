import json

import yaml

from qe_skill.m2 import analyze_project
from qe_skill.m3 import generate_m3
from qe_skill.m3_render import render_html, render_json, render_markdown, render_yaml

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
