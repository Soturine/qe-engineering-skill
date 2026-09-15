"""Pure renderers for canonical M3 artifacts; no analysis logic or external I/O."""

import html
import json

import yaml

from qe_skill.m3 import M3GenerationReport


def render_json(report: M3GenerationReport) -> str:
    return (
        json.dumps(
            report.model_dump(mode="json"),
            indent=2,
            sort_keys=True,
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )


def render_yaml(report: M3GenerationReport) -> str:
    return yaml.safe_dump(
        report.model_dump(mode="json"), sort_keys=True, allow_unicode=True, default_flow_style=False
    )


def render_markdown(report: M3GenerationReport) -> str:
    lines = [
        "# M3 Test Generation Report",
        "",
        f"- Mode: `{report.mode}`",
        f"- Status: `{report.status}`",
        f"- Project/snapshot: `{report.project_id}` / `{report.snapshot_id}`",
        f"- Proposal only: `{str(report.proposal_only).lower()}`",
        "",
        "## Test proposals",
        "",
    ]
    for case in report.cases:
        lines.extend(
            [
                f"### {case.title}",
                "",
                f"Readiness: `{case.readiness}` — {case.rationale}",
                "",
                f"Objective: {case.objective.text or 'Unresolved'}",
                "",
            ]
        )
        for step in case.steps:
            lines.append(
                f"{step.number}. {step.action.text or 'Blocked action'} → "
                f"{step.expected_result or 'No normative Expected Result'}"
            )
        if case.blocking_notes:
            lines.extend(
                ["", "Blocking/review notes:"] + [f"- {note}" for note in case.blocking_notes]
            )
        lines.append("")
    lines.extend(["## Brownfield/clone proposals", ""])
    for revision in report.revisions:
        lines.append(
            f"- `{revision.original_test.id}` → `{revision.action}`: {revision.rationale} "
            f"({len(revision.field_diffs)} field diffs, {len(revision.step_diffs)} step diffs)"
        )
    lines.extend(["", "## Shared Steps", ""])
    lines.extend(f"- {item.title} (`{item.readiness}`)" for item in report.shared_steps)
    lines.extend(["", "## Parameters", ""])
    lines.extend(f"- {item.name}: {item.rationale}" for item in report.parameters)
    lines.extend(["", "## Traceability", ""])
    lines.extend(
        f"- `{edge.source.id}` → `{edge.target.id}` (`{edge.relation}`)"
        for edge in report.traceability
    )
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {item}" for item in report.limitations)
    return "\n".join(lines).rstrip() + "\n"


def render_html(report: M3GenerationReport) -> str:
    def esc(value: object) -> str:
        return html.escape(str(value), quote=True)

    cases = "".join(
        "<article><h2>"
        + esc(case.title)
        + "</h2><p><strong>Readiness:</strong> "
        + esc(case.readiness)
        + "</p><p><strong>Objective:</strong> "
        + esc(case.objective.text or "Unresolved")
        + "</p><ol>"
        + "".join(
            "<li>"
            + esc(step.action.text or "Blocked action")
            + " <strong>Expected:</strong> "
            + esc(step.expected_result or "No normative Expected Result")
            + "</li>"
            for step in case.steps
        )
        + "</ol><ul>"
        + "".join(f"<li>{esc(note)}</li>" for note in case.blocking_notes)
        + "</ul></article>"
        for case in report.cases
    )
    revisions = "".join(
        f"<li>{esc(item.original_test.id)} → {esc(item.action)}: {esc(item.rationale)}</li>"
        for item in report.revisions
    )
    shared = "".join(f"<li>{esc(item.title)}</li>" for item in report.shared_steps)
    parameters = "".join(f"<li>{esc(item.name)}</li>" for item in report.parameters)
    traceability = "".join(
        f"<li>{esc(item.source.id)} → {esc(item.target.id)} ({esc(item.relation)})</li>"
        for item in report.traceability
    )
    limitations = "".join(f"<li>{esc(item)}</li>" for item in report.limitations)
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        "<title>M3 Test Generation Report</title>"
        "<style>body{font:16px system-ui;max-width:70rem;margin:auto;padding:2rem}"
        "article{border-top:1px solid #ccc}</style></head><body>"
        f"<h1>M3 Test Generation Report</h1><p>Mode: {esc(report.mode)} | "
        f"Snapshot: {esc(report.snapshot_id)} | Status: {esc(report.status)}</p>"
        f"{cases}<h2>Brownfield/clone proposals</h2><ul>{revisions}</ul>"
        f"<h2>Shared Steps</h2><ul>{shared}</ul><h2>Parameters</h2><ul>{parameters}</ul>"
        f"<h2>Traceability</h2><ul>{traceability}</ul>"
        f"<h2>Limitations</h2><ul>{limitations}</ul></body></html>\n"
    )
