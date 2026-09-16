"""Local M4 orchestration workspace for agents and deterministic fallback."""

from __future__ import annotations

import fnmatch
import hashlib
import html
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

import yaml
from pydantic import Field

from qe_skill import __version__
from qe_skill import domain as d
from qe_skill.clarification import ClarificationSet, questions_from_normalization
from qe_skill.grilling import ScenarioGrill, grill_scenarios
from qe_skill.ingestion import IngestionReport, ingest_local
from qe_skill.m2 import AnalysisConfig, M2AnalysisReport, analyze_project
from qe_skill.m3 import AuthoringConfig, M3GenerationReport, generate_m3
from qe_skill.normalization import (
    SemanticNormalizationSet,
    detect_source_language,
    normalize_candidate_set,
)
from qe_skill.reasoning import (
    EvidenceExcerpt,
    ProviderIdentity,
    ProviderResponse,
    ReasoningRequest,
    ReasoningResult,
    StaticReasoningProvider,
    canonical_hash,
    run_reasoning,
)
from qe_skill.semantic import SemanticCandidateSet, materialize_provider_candidates

SemanticMode = Literal["agent-runtime", "external-provider", "deterministic-only"]
RunStatus = Literal["AWAITING_AGENT", "COMPLETE", "PARTIAL", "BLOCKED"]
SourceRole = Literal["REQUIREMENTS", "IMPLEMENTATION", "TEST", "SUPPORTING", "IGNORE"]


class ScopeRule(d.Record):
    role: SourceRole
    pattern: d.Text
    explicit: bool = True


class ScopedSource(d.Record):
    source: d.Ref
    path: d.Text
    role: SourceRole
    basis: Literal["EXPLICIT", "HEURISTIC"]
    reason: d.Text


class RunScope(d.Artifact):
    root: d.Text
    rules: list[ScopeRule]
    sources: list[ScopedSource]
    ambiguities: list[d.Text]
    authority_assigned: Literal[False] = False


class QERun(d.Artifact):
    run_id: d.Text
    engine_version: d.Text
    semantic_mode: SemanticMode
    status: RunStatus
    root: d.Text
    workspace: d.Text
    scope: RunScope
    ingestion: IngestionReport
    reasoning_request: ReasoningRequest | None = None
    reasoning_result: ReasoningResult | None = None
    candidates: SemanticCandidateSet | None = None
    normalization: SemanticNormalizationSet | None = None
    clarifications: ClarificationSet | None = None
    analysis: M2AnalysisReport | None = None
    scenario_grill: ScenarioGrill | None = None
    generation: M3GenerationReport | None = None
    limitations: list[d.Text] = Field(default_factory=list)
    network_used: bool = False
    external_writes: Literal[False] = False
    proposal_only: Literal[True] = True


def _slug(value: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9._-]+", "-", value).strip("-.")
    return clean[:48] or "project"


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def _heuristic_role(path: str) -> tuple[SourceRole, str]:
    lower = path.casefold()
    name = Path(lower).name
    if any(part in lower for part in ("test", "spec", "e2e", "fixture")):
        return "TEST", "Path name suggests a test asset; review this non-authoritative role."
    if Path(lower).suffix in {".py"} or any(part in lower for part in ("src/", "app/")):
        return "IMPLEMENTATION", "Path/type suggests implementation; review this role."
    if any(
        part in name
        for part in ("requirement", "requisito", "prd", "acceptance", "criterio", "critério")
    ):
        return "REQUIREMENTS", "Path name suggests requirements; review this role."
    return "SUPPORTING", "No explicit role matched; retained as supporting evidence."


def build_scope(
    ingestion: IngestionReport,
    *,
    root: Path,
    requirements: tuple[str, ...] = (),
    implementation: tuple[str, ...] = (),
    tests: tuple[str, ...] = (),
    ignore: tuple[str, ...] = (),
) -> RunScope:
    """Classify source purpose without assigning normative authority."""

    rules = [ScopeRule(role="REQUIREMENTS", pattern=value) for value in requirements]
    rules += [ScopeRule(role="IMPLEMENTATION", pattern=value) for value in implementation]
    rules += [ScopeRule(role="TEST", pattern=value) for value in tests]
    rules += [ScopeRule(role="IGNORE", pattern=value) for value in ignore]
    scoped: list[ScopedSource] = []
    ambiguities: list[str] = []
    for source in ingestion.ledger.sources:
        path = source.locator
        matches = [rule for rule in rules if _matches(path, (rule.pattern,))]
        if matches:
            roles = {rule.role for rule in matches}
            if len(roles) > 1:
                ambiguities.append(
                    f"{path}: explicit role patterns conflict ({', '.join(sorted(roles))})."
                )
                role: SourceRole = "SUPPORTING"
                reason = "Conflicting explicit role patterns; retained as supporting evidence."
            else:
                role = matches[0].role
                reason = f"Matched explicit {role.lower()} pattern."
            basis: Literal["EXPLICIT", "HEURISTIC"] = "EXPLICIT"
        else:
            role, reason = _heuristic_role(path)
            basis = "HEURISTIC"
        scoped.append(
            ScopedSource(
                source=d.Ref(
                    id=source.id, project_id=source.project_id, snapshot_id=source.snapshot_id
                ),
                path=path,
                role=role,
                basis=basis,
                reason=reason,
            )
        )
    return RunScope(
        id="run-scope",
        project_id=ingestion.project_id,
        snapshot_id=ingestion.snapshot_id,
        root=str(root),
        rules=rules,
        sources=scoped,
        ambiguities=ambiguities,
    )


def _reasoning_request(ingestion: IngestionReport, scope: RunScope) -> ReasoningRequest | None:
    roles = {item.source.id: item.role for item in scope.sources}
    sources = {item.id: item for item in ingestion.ledger.sources}
    excerpts: list[EvidenceExcerpt] = []
    total = 0
    for parsed in ingestion.parses:
        source = sources.get(parsed.source.id)
        if source is None or source.study_status != "STUDIED" or roles.get(source.id) == "IGNORE":
            continue
        for extraction in parsed.extractions:
            if len(excerpts) >= 64:
                break
            text = extraction.text[:20_000]
            if total + len(text) > 200_000:
                break
            total += len(text)
            language, _confidence = detect_source_language(text)
            excerpt_seed = source.locator + extraction.location + extraction.source_hash
            excerpts.append(
                EvidenceExcerpt(
                    id=f"excerpt.{hashlib.sha256(excerpt_seed.encode()).hexdigest()[:24]}",
                    project_id=ingestion.project_id,
                    snapshot_id=ingestion.snapshot_id,
                    source=extraction.source.model_copy(deep=True),
                    source_hash=extraction.source_hash,
                    location=extraction.location,
                    span=(
                        d.Ref(
                            id=extraction.span.id,
                            project_id=extraction.span.project_id,
                            snapshot_id=extraction.span.snapshot_id,
                        )
                        if extraction.span
                        else None
                    ),
                    text=text,
                    source_language=language,
                )
            )
    if not excerpts:
        return None
    seed = json.dumps([item.id for item in excerpts], separators=(",", ":"))
    return ReasoningRequest(
        id=f"reasoning-request.{hashlib.sha256(seed.encode()).hexdigest()[:24]}",
        project_id=ingestion.project_id,
        snapshot_id=ingestion.snapshot_id,
        operation="EXTRACT",
        excerpts=excerpts,
        prompt_version="m4.agent-runtime.v1",
        configuration_hash=hashlib.sha256(b"m4.agent-runtime.v1").hexdigest(),
    )


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _markdown(run: QERun) -> str:
    generation = run.generation
    questions = run.clarifications.questions if run.clarifications else []
    probes = run.scenario_grill.probes if run.scenario_grill else []
    cases = generation.cases if generation else []
    lines = [
        "# QE Engineering — Local Review",
        "",
        f"- Status: `{run.status}`",
        f"- Semantic mode: `{run.semantic_mode}`",
        f"- Evidence: {len(run.ingestion.ledger.sources)} source(s)",
        f"- Semantic candidates: {len(run.candidates.candidates) if run.candidates else 0}",
        f"- Open questions: {sum(item.status == 'OPEN' for item in questions) + len(probes)}",
        f"- Test Case proposals: {len(cases)}",
        "",
        "## Scope and evidence",
        "",
    ]
    for item in run.scope.sources:
        lines.append(f"- `{item.path}` — {item.role} ({item.basis.lower()})")
    lines += ["", "## Understanding and review", ""]
    if run.status == "AWAITING_AGENT":
        lines.append(
            "The bounded `agent-request.json` is ready for semantic interpretation by the agent."
        )
    for question in questions:
        lines.append(f"- **{question.status}** {question.question} — {question.reason}")
    for probe in probes:
        lines.append(f"- **OPEN** {probe.question} — {probe.rationale}")
    if not questions and not probes and run.status != "AWAITING_AGENT":
        lines.append("No semantic clarification question was produced.")
    lines += ["", "## Test Cases", ""]
    if not cases:
        lines.append("No Test Case proposal was materialized from the defensible Project Model.")
    for case in cases:
        lines += [f"### {case.title}", "", f"Readiness: `{case.readiness}`", ""]
        for step in case.steps:
            lines.append(f"{step.number}. {step.action.text or '[blocked action]'}")
            if step.expected_result:
                lines.append(f"   - Expected: {step.expected_result}")
        for note in case.blocking_notes:
            lines.append(f"- Blocker: {note}")
        lines.append("")
    lines += ["## Limitations", ""]
    lines.extend(f"- {item}" for item in run.limitations)
    return "\n".join(lines).rstrip() + "\n"


def _html_report(markdown: str, run: QERun) -> str:
    body = html.escape(markdown)
    return (
        '<!doctype html><html lang="pt-BR"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>QE Engineering — {html.escape(run.run_id)}</title>"
        "<style>body{font:16px/1.55 system-ui;max-width:1100px;margin:auto;padding:2rem;"
        "background:#f7f8fa;color:#18202a}pre{white-space:pre-wrap;background:white;padding:2rem;"
        "border:1px solid #d9dee7;border-radius:12px}</style>"
        f"<body><pre>{body}</pre></body></html>"
    )


def write_run_workspace(run: QERun, root: Path) -> Path:
    workspace_root = root / ".qe"
    run_dir = workspace_root / "runs" / run.run_id
    value = run.model_dump(mode="json")
    _atomic_write(run_dir / "run.json", json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    _atomic_write(
        run_dir / "scope.json",
        json.dumps(run.scope.model_dump(mode="json"), ensure_ascii=False, indent=2) + "\n",
    )
    if run.reasoning_request:
        _atomic_write(
            run_dir / "agent-request.json",
            json.dumps(run.reasoning_request.model_dump(mode="json"), ensure_ascii=False, indent=2)
            + "\n",
        )
    if run.clarifications:
        _atomic_write(
            run_dir / "questions.json",
            json.dumps(run.clarifications.model_dump(mode="json"), ensure_ascii=False, indent=2)
            + "\n",
        )
    if run.scenario_grill:
        _atomic_write(
            run_dir / "scenario-grill.json",
            json.dumps(
                run.scenario_grill.model_dump(mode="json"), ensure_ascii=False, indent=2
            )
            + "\n",
        )
    markdown = _markdown(run)
    _atomic_write(workspace_root / "report.md", markdown)
    _atomic_write(workspace_root / "report.html", _html_report(markdown, run))
    tests = (
        [item.model_dump(mode="json") for item in run.generation.cases] if run.generation else []
    )
    _atomic_write(
        workspace_root / "test-cases.yaml",
        yaml.safe_dump(tests, allow_unicode=True, sort_keys=False),
    )
    _atomic_write(
        workspace_root / "latest.json",
        json.dumps({"run_id": run.run_id, "status": run.status, "path": str(run_dir)}, indent=2)
        + "\n",
    )
    return run_dir


def execute_run(
    root: Path,
    *,
    semantic_mode: SemanticMode = "agent-runtime",
    agent_response: ProviderResponse | None = None,
    requirements: tuple[str, ...] = (),
    implementation: tuple[str, ...] = (),
    tests: tuple[str, ...] = (),
    ignore: tuple[str, ...] = (),
    project_locale: d.LanguageCode = "und",
    output_language: d.OutputLanguage = "source",
) -> QERun:
    resolved = root.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError("qe run requires an existing project directory")
    created = datetime.now(UTC).replace(microsecond=0)
    run_seed = f"{resolved}\0{created.isoformat()}\0{os.getpid()}"
    run_suffix = hashlib.sha256(run_seed.encode()).hexdigest()[:8]
    run_id = f"run-{created.strftime('%Y%m%dT%H%M%SZ')}-{run_suffix}"
    project_id = _slug(resolved.name)
    snapshot_id = run_id
    ingestion = ingest_local(
        resolved,
        project_id=project_id,
        snapshot_id=snapshot_id,
        collected_at=created.strftime("%Y-%m-%dT%H:%M:%SZ"),
        excludes=ignore,
    )
    ingestion.ledger.manifest.project_locale = project_locale
    ingestion.ledger.manifest.output_language = output_language
    ingestion.build.model.ledger = ingestion.ledger
    scope = build_scope(
        ingestion,
        root=resolved,
        requirements=requirements,
        implementation=implementation,
        tests=tests,
        ignore=ignore,
    )
    request = _reasoning_request(ingestion, scope)
    reasoning_result: ReasoningResult | None = None
    candidates: SemanticCandidateSet | None = None
    normalization: SemanticNormalizationSet | None = None
    clarifications: ClarificationSet | None = None
    limitations: list[str] = []
    if request and agent_response:
        known = {item.id for item in request.excerpts}
        cited = {
            identifier
            for proposal in agent_response.proposals
            for identifier in proposal.source_excerpt_ids
        }
        unknown = sorted(cited - known)
        if unknown:
            raise ValueError(f"agent response cites unknown excerpt ids: {', '.join(unknown)}")
        provider = StaticReasoningProvider(
            ProviderIdentity(
                provider="agent-runtime",
                model="runtime-supplied",
                model_version="unreported",
                adapter_version="1.0",
            ),
            {"EXTRACT": agent_response},
        )
        reasoning_result = run_reasoning(request, provider)
        candidates = materialize_provider_candidates(
            request,
            reasoning_result,
            ingestion.ledger,
            run_id=run_id,
            created_at=created.strftime("%Y-%m-%dT%H:%M:%SZ"),
            extractor_version="1.0",
        )
        normalization = normalize_candidate_set(
            candidates,
            request,
            reasoning_result,
            ingestion.ledger,
            project_locale=project_locale,
            output_language=output_language,
        )
        clarifications = questions_from_normalization(normalization, candidates)
        limitations.append(
            "Agent interpretations remain review candidates and do not become normative "
            "Project Model facts."
        )
    elif request:
        reasoning_result = run_reasoning(request)
        if semantic_mode == "external-provider":
            limitations.append("No external provider adapter or response was configured.")
        elif semantic_mode == "agent-runtime":
            limitations.append(
                "Awaiting a provenance-bound agent response in agent-response.json format."
            )
        else:
            limitations.append("Deterministic-only mode did not request semantic interpretation.")
    model = ingestion.build.model
    analysis: M2AnalysisReport | None = None
    scenario_grill: ScenarioGrill | None = None
    generation: M3GenerationReport | None = None
    try:
        analysis = analyze_project(model, AnalysisConfig())
        scenario_grill = grill_scenarios(analysis, model)
        generation = generate_m3(model, analysis, AuthoringConfig())
    except ValueError as error:
        limitations.append(f"Downstream analysis/generation blocked: {error}")
    awaiting = semantic_mode == "agent-runtime" and request is not None and agent_response is None
    if awaiting:
        status: RunStatus = "AWAITING_AGENT"
    elif ingestion.status == "INVALID" or (analysis is not None and analysis.status == "INVALID"):
        status = "BLOCKED"
    elif ingestion.status == "PARTIAL" or scope.ambiguities or limitations:
        status = "PARTIAL"
    else:
        status = "COMPLETE"
    run = QERun(
        id="qe-run",
        project_id=project_id,
        snapshot_id=snapshot_id,
        run_id=run_id,
        engine_version=__version__,
        semantic_mode=semantic_mode,
        status=status,
        root=str(resolved),
        workspace=str(resolved / ".qe" / "runs" / run_id),
        scope=scope,
        ingestion=ingestion,
        reasoning_request=request,
        reasoning_result=reasoning_result,
        candidates=candidates,
        normalization=normalization,
        clarifications=clarifications,
        analysis=analysis,
        scenario_grill=scenario_grill,
        generation=generation,
        limitations=limitations,
        network_used=agent_response.network_used if agent_response else False,
    )
    write_run_workspace(run, resolved)
    return run


def load_agent_response(path: Path) -> ProviderResponse:
    value = json.loads(path.read_text(encoding="utf-8"))
    return ProviderResponse.model_validate(value)


def run_fingerprint(run: QERun) -> str:
    """Stable diagnostic fingerprint excluding the timestamped run identity."""

    return canonical_hash(run.scope)
