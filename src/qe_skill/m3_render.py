"""Deterministic, component-oriented renderers for canonical M3 artifacts."""

# HTML fragments remain readable as complete literals; wrapping them obscures component output.
# ruff: noqa: E501

from __future__ import annotations

import html
import json
from collections.abc import Mapping
from typing import Literal

import yaml
from pydantic import Field

from qe_skill import domain as d
from qe_skill.m3 import M3GenerationReport

RenderFormat = Literal["json", "yaml", "markdown", "html"]


class ReportTheme(d.Record):
    project_name: str | None = None
    accent: str = Field(default="#2563eb", pattern=r"^#[0-9a-fA-F]{6}$")
    density: Literal["compact", "comfortable"] = "comfortable"


def _payload(report: M3GenerationReport | Mapping[str, object]) -> dict[str, object]:
    value = (
        report.model_dump(mode="json") if isinstance(report, M3GenerationReport) else dict(report)
    )
    version = value.get("schema_version")
    if not isinstance(version, str) or version.split(".", 1)[0] != "1":
        raise ValueError("Unsupported M3 report schema major version.")
    return value


def _items(value: object) -> list[dict[str, object]]:
    return (
        [dict(item) for item in value if isinstance(item, Mapping)]
        if isinstance(value, list)
        else []
    )


def _list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _mapping(value: object) -> dict[str, object]:
    return {str(key): item for key, item in value.items()} if isinstance(value, Mapping) else {}


def _ref_id(value: object) -> str:
    return str(value.get("id", "unresolved")) if isinstance(value, Mapping) else "unresolved"


def _text(value: object, default: str = "Unresolved") -> str:
    if isinstance(value, Mapping):
        text = value.get("text")
        return str(text) if text else default
    return str(value) if value else default


def render_json(report: M3GenerationReport | Mapping[str, object]) -> str:
    return (
        json.dumps(_payload(report), indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
        + "\n"
    )


def render_yaml(report: M3GenerationReport | Mapping[str, object]) -> str:
    return yaml.safe_dump(
        _payload(report), sort_keys=True, allow_unicode=True, default_flow_style=False
    )


def _markdown_cases(data: dict[str, object]) -> list[str]:
    lines = ["## Test Cases", ""]
    for case in _items(data.get("cases")):
        lines.extend(
            [
                f"### {case.get('title', 'Untitled')}",
                "",
                f"Readiness: `{case.get('readiness', 'UNKNOWN')}`",
                "",
                f"Objective: {_text(case.get('objective'))}",
                "",
            ]
        )
        for step in _items(case.get("steps")):
            lines.append(
                f"{step.get('number', '?')}. {_text(step.get('action'), 'Blocked action')} → "
                f"{step.get('expected_result') or 'No normative Expected Result'}"
            )
        shared = (
            [_ref_id(item) for item in _list(case.get("shared_step_candidates"))]
            if isinstance(case.get("shared_step_candidates"), list)
            else []
        )
        params = (
            [_ref_id(item) for item in _list(case.get("parameter_candidates"))]
            if isinstance(case.get("parameter_candidates"), list)
            else []
        )
        if shared:
            lines.extend(["", "Shared Steps: " + ", ".join(f"`{item}`" for item in shared)])
        if params:
            lines.extend(["", "Parameters: " + ", ".join(f"`{{{item}}}`" for item in params)])
        notes = case.get("blocking_notes")
        if isinstance(notes, list) and notes:
            lines.extend(["", "Blocking/review notes:"] + [f"- {note}" for note in notes])
        lines.append("")
    return lines


def render_markdown(report: M3GenerationReport | Mapping[str, object]) -> str:
    data = _payload(report)
    lines = [
        "# M3 Test Generation Report",
        "",
        f"- Mode: `{data.get('mode', 'UNKNOWN')}`",
        f"- Status: `{data.get('status', 'UNKNOWN')}`",
        f"- Project/snapshot: `{data.get('project_id')}` / `{data.get('snapshot_id')}`",
        "",
        *_markdown_cases(data),
    ]
    sections = (
        ("Shared Steps", "shared_steps"),
        ("Parameters", "parameters"),
        ("Brownfield Changes", "revisions"),
        ("Traceability", "traceability"),
    )
    for title, key in sections:
        items = _items(data.get(key))
        if items:
            formatted: list[str] = []
            for item in items:
                if key == "shared_steps":
                    rendered = f"{item.get('title')} (`{item.get('readiness')}`)"
                elif key == "parameters":
                    rendered = f"{item.get('name')}: {item.get('rationale')}"
                elif key == "revisions":
                    rendered = (
                        f"`{_ref_id(item.get('original_test'))}` → "
                        f"`{item.get('action')}`: {item.get('rationale')}"
                    )
                else:
                    rendered = (
                        f"`{_ref_id(item.get('source'))}` → "
                        f"`{_ref_id(item.get('target'))}` (`{item.get('relation')}`)"
                    )
                formatted.append(f"- {rendered}")
            lines.extend([f"## {title}", "", *formatted, ""])
    limitations = data.get("limitations")
    if isinstance(limitations, list) and limitations:
        lines.extend(["## Risks & Gaps", "", *(f"- {item}" for item in limitations), ""])
    return "\n".join(lines).rstrip() + "\n"


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _html_section(identifier: str, title: str, body: str) -> str:
    return (
        f'<section id="{_esc(identifier)}"><h2>{_esc(title)}</h2>{body}</section>' if body else ""
    )


def _html_cases(
    data: dict[str, object],
    shared_by_id: dict[str, dict[str, object]],
    parameter_by_id: dict[str, dict[str, object]],
) -> str:
    output: list[str] = []
    for case in _items(data.get("cases")):
        case_id = str(case.get("id", "case"))
        steps = "".join(
            f'<li><span class="phase">{_esc(step.get("phase") or "STEP")}</span> '
            f"{_esc(_text(step.get('action'), 'Blocked action'))}"
            + (
                f"<div><strong>Expected:</strong> {_esc(step.get('expected_result'))}</div>"
                if step.get("expected_result")
                else ""
            )
            + "</li>"
            for step in _items(case.get("steps"))
        )
        shared_cards = (
            "".join(
                f'<a class="chip" href="#shared-{_esc(ref_id)}">{_esc(ref_id)} — {_esc(shared_by_id.get(ref_id, {}).get("title", "Shared Step"))}</a>'
                for ref_id in (
                    _ref_id(item)
                    for item in _list(case.get("shared_step_candidates"))
                    if isinstance(item, Mapping)
                )
            )
            if isinstance(case.get("shared_step_candidates"), list)
            else ""
        )
        parameter_cards = (
            "".join(
                f'<a class="chip" href="#parameter-{_esc(ref_id)}">{{{_esc(parameter_by_id.get(ref_id, {}).get("name", ref_id))}}}</a>'
                for ref_id in (
                    _ref_id(item)
                    for item in _list(case.get("parameter_candidates"))
                    if isinstance(item, Mapping)
                )
            )
            if isinstance(case.get("parameter_candidates"), list)
            else ""
        )
        notes = "".join(f"<li>{_esc(item)}</li>" for item in _list(case.get("blocking_notes")))
        output.append(
            f'<article id="case-{_esc(case_id)}"><h3>{_esc(case.get("title", "Untitled"))}</h3>'
            f'<span class="status">{_esc(case.get("readiness", "UNKNOWN"))}</span>'
            f"<p><strong>Objective:</strong> {_esc(_text(case.get('objective')))}</p><ol>{steps}</ol>"
            f"{shared_cards}{parameter_cards}{('<h4>Blockers</h4><ul>' + notes + '</ul>') if notes else ''}</article>"
        )
    return "".join(output)


def render_html(
    report: M3GenerationReport | Mapping[str, object], theme: ReportTheme | None = None
) -> str:
    data = _payload(report)
    theme = theme or ReportTheme()
    shared = _items(data.get("shared_steps"))
    parameters = _items(data.get("parameters"))
    revisions = _items(data.get("revisions"))
    traceability = _items(data.get("traceability"))
    shared_by_id = {str(item.get("id")): item for item in shared}
    parameter_by_id = {str(item.get("id")): item for item in parameters}
    shared_html = "".join(
        f'<article id="shared-{_esc(item.get("id"))}"><h3>{_esc(item.get("title"))}</h3>'
        f"<p>{_esc(item.get('readiness'))}; definition reusable, execution results remain per Test Case.</p>"
        + "<ol>"
        + "".join(
            f"<li>{_esc(_text(step.get('action'), 'Blocked action'))}</li>"
            for step in _items(item.get("steps"))
        )
        + "</ol>"
        + f"<p>Evidence: {', '.join(_esc(_ref_id(ref)) for ref in _list(item.get('supporting_evidence'))) or 'Unresolved'}</p>"
        + f"<p>Paths: {', '.join(_esc(_ref_id(ref)) for ref in _list(item.get('path_refs'))) or 'Unresolved'}</p>"
        + f"<p>Claims: {', '.join(_esc(_ref_id(ref)) for ref in _list(item.get('claim_refs'))) or 'Unresolved'}</p>"
        + f"<p>Used by: {', '.join(_esc(_ref_id(ref)) for ref in _list(item.get('used_by')))}</p></article>"
        for item in shared
    )
    parameter_html = "".join(
        f'<article id="parameter-{_esc(item.get("id"))}"><h3>{_esc(item.get("name"))}</h3>'
        f"<p>Properties: {_esc(_text(item.get('properties')))}</p>"
        f"<p>Constraints: {_esc(', '.join(_ref_id(value) for value in _list(item.get('constraints'))) or 'Unresolved')}</p>"
        f"<p>Partitions: {_esc(', '.join(str(value) for value in _list(item.get('partitions'))) or 'Unresolved')}</p>"
        f"<p>Values: {_esc(', '.join(str(value) for value in _list(item.get('candidate_values'))) or 'No value invented')}</p>"
        f"<p>Sources: {_esc(', '.join(_ref_id(value) for value in _list(item.get('source_evidence'))) or 'Unresolved')}</p>"
        f"<p>Used by: {_esc(', '.join(_ref_id(value) for value in _list(item.get('used_by'))) or 'Unresolved')}</p></article>"
        for item in parameters
    )
    revision_html = "".join(
        f'<article><h3>{_esc(_ref_id(item.get("original_test")))}</h3><div class="compare">'
        f"<div><h4>Original</h4><pre>{_esc(item.get('original_text', 'Unavailable'))}</pre></div>"
        f"<div><h4>Proposed</h4><p>{_esc(item.get('action'))} — {_esc(item.get('readiness'))}</p></div></div>"
        "<p><strong>Historical asset modified? NO</strong></p>"
        + "".join(
            f"<p>{_esc(diff.get('field'))}: {_esc(diff.get('rationale'))}</p>"
            for diff in _items(item.get("field_diffs"))
        )
        + "</article>"
        for item in revisions
    )
    trace_html = "".join(
        f'<li><a href="#case-{_esc(_ref_id(item.get("target")))}">{_esc(_ref_id(item.get("source")))} → {_esc(_ref_id(item.get("target")))}</a> ({_esc(item.get("relation"))})</li>'
        for item in traceability
    )
    gaps = "".join(f"<li>{_esc(item)}</li>" for item in _list(data.get("limitations")))
    binding = _mapping(data.get("input_binding"))
    manifest = _mapping(data.get("manifest"))
    configuration = _mapping(manifest.get("configuration"))
    generation = "".join(
        f"<li>{_esc(key)}: <code>{_esc(value)}</code></li>"
        for key, value in sorted(binding.items())
    )
    generation += "".join(
        f"<li>configuration.{_esc(key)}: <code>{_esc(value)}</code></li>"
        for key, value in sorted(configuration.items())
    )
    generation += "".join(
        f"<li>{_esc(key)}: <code>{_esc(manifest.get(key))}</code></li>"
        for key in ("created_at", "tool_version")
        if manifest.get(key) is not None
    )
    nav_items = [("cases", "Test Cases")]
    nav_items += [("shared", "Shared Steps")] if shared else []
    nav_items += [("parameters", "Parameters")] if parameters else []
    nav_items += [("changes", "Brownfield Changes")] if revisions else []
    nav_items += [("trace", "Traceability")] if traceability else []
    nav_items += [("gaps", "Risks & Gaps")] if gaps else []
    nav_items += [("generation", "Generation Info")]
    navigation = "".join(f'<a href="#{key}">{title}</a>' for key, title in nav_items)
    title = theme.project_name or "M3 Test Generation Report"
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        f"<title>{_esc(title)}</title><style>:root{{--accent:{theme.accent}}}"
        "body{font:16px system-ui;max-width:76rem;margin:auto;padding:2rem;line-height:1.5}"
        "nav{display:flex;gap:1rem;flex-wrap:wrap}section{border-top:1px solid #ccc;margin-top:2rem}"
        "article{padding:1rem 0}.status,.chip{display:inline-block;padding:.2rem .5rem;margin:.2rem;"
        "border:1px solid var(--accent);border-radius:.3rem}.compare{display:grid;grid-template-columns:1fr 1fr;gap:1rem}"
        "body[data-density=compact] article{padding:.35rem 0}pre{white-space:pre-wrap}"
        "@media(max-width:700px){.compare{grid-template-columns:1fr}}</style></head>"
        f'<body data-density="{_esc(theme.density)}">'
        f"<header><h1>{_esc(title)}</h1><p>Mode: {_esc(data.get('mode'))} | Snapshot: {_esc(data.get('snapshot_id'))} | Status: {_esc(data.get('status'))}</p><nav>{navigation}</nav></header>"
        + _html_section("cases", "Test Cases", _html_cases(data, shared_by_id, parameter_by_id))
        + _html_section("shared", "Shared Steps", shared_html)
        + _html_section("parameters", "Parameters", parameter_html)
        + _html_section("changes", "Brownfield Changes", revision_html)
        + _html_section("trace", "Traceability", f"<ul>{trace_html}</ul>" if trace_html else "")
        + _html_section("gaps", "Risks & Gaps", f"<ul>{gaps}</ul>" if gaps else "")
        + _html_section(
            "generation",
            "Generation Info",
            f"<ul><li>project_id: {_esc(data.get('project_id'))}</li><li>snapshot_id: {_esc(data.get('snapshot_id'))}</li>{generation}</ul>",
        )
        + "</body></html>\n"
    )


def render_canonical(
    report: Mapping[str, object], output_format: RenderFormat, theme: ReportTheme | None = None
) -> str:
    renderers = {"json": render_json, "yaml": render_yaml, "markdown": render_markdown}
    return (
        render_html(report, theme) if output_format == "html" else renderers[output_format](report)
    )
