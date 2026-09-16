"""Deterministic, component-oriented renderers for canonical M3 artifacts."""

# HTML fragments remain readable as complete literals; wrapping them obscures component output.
# ruff: noqa: E501

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Literal

import yaml
from pydantic import Field

from qe_skill import domain as d
from qe_skill.m3 import M3GenerationReport
from qe_skill.review import PT, ReviewContext, localize_presentation_text, review_html

RenderFormat = Literal["json", "yaml", "markdown", "html"]


class ReportTheme(d.Record):
    project_name: str | None = None
    accent: str = Field(default="#2563eb", pattern=r"^#[0-9a-fA-F]{6}$")
    density: Literal["compact", "comfortable"] = "comfortable"
    project_locale: d.LanguageCode | None = None
    output_language: d.OutputLanguage | None = None


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


def render_markdown(
    report: M3GenerationReport | Mapping[str, object], theme: ReportTheme | None = None
) -> str:
    data = _payload(report)
    if resolve_language(data, theme or ReportTheme()) == "pt-BR":

        def localized(value: object, depth: int = 0, field: str = "") -> list[str]:
            if isinstance(value, dict):
                output = []
                for key, child in value.items():
                    output.append("  " * depth + f"- {PT.get(key, key)}:")
                    output.extend(localized(child, depth + 1, key))
                return output
            if isinstance(value, list):
                return [line for child in value for line in localized(child, depth, field)]
            text = localize_presentation_text(str(value), field, "pt-BR")
            return ["  " * depth + "- " + text]

        return "# Plano de Testes\n\n" + "\n".join(localized(data)) + "\n"
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


def render_html(
    report: M3GenerationReport | Mapping[str, object],
    theme: ReportTheme | None = None,
    *,
    context: ReviewContext | None = None,
) -> str:
    data = _payload(report)
    theme = theme or ReportTheme()
    if context:
        context.validate_for(M3GenerationReport.model_validate(data))
    language = resolve_language(data, theme, context)
    title = theme.project_name or ("Plano de Testes" if language == "pt-BR" else "Test Plan")
    return review_html(
        data,
        language=language,
        title=title,
        accent=theme.accent,
        density=theme.density,
        context=context,
    )


def resolve_language(
    data: dict[str, object], theme: ReportTheme, context: ReviewContext | None = None
) -> str:
    config = _mapping(_mapping(data.get("manifest")).get("configuration"))
    manifest = context.project_model.ledger.manifest if context else None
    locale = theme.project_locale or (
        manifest.project_locale if manifest else config.get("project_locale")
    )
    output = theme.output_language or (
        manifest.output_language if manifest else config.get("output_language")
    )
    return str(output) if output in {"pt-BR", "en"} else ("pt-BR" if locale == "pt-BR" else "en")


def render_canonical(
    report: Mapping[str, object],
    output_format: RenderFormat,
    theme: ReportTheme | None = None,
    *,
    context: ReviewContext | None = None,
) -> str:
    if output_format == "markdown":
        return render_markdown(report, theme)
    renderers = {"json": render_json, "yaml": render_yaml}
    return (
        render_html(report, theme, context=context)
        if output_format == "html"
        else renderers[output_format](report)
    )
