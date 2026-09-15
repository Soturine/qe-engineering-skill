"""End-to-end local M1 ingestion orchestration with explicit partial states."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field

from qe_skill import domain as d
from qe_skill.integrity import validate_project_model
from qe_skill.inventory import (
    InventoryEntry,
    InventoryLimits,
    InventoryReport,
    inventory_sources,
    ledger_from_inventory,
)
from qe_skill.parsers import PARSER_VERSION, ParseResult, ParserLimits, parse_entry
from qe_skill.project_builder import ProjectBuild, build_project_model


class DocumentExtractionAdapter(Protocol):
    """Boundary for future bounded document extractors; no adapter is enabled implicitly."""

    def parse(self, root: Path, entry: InventoryEntry, limits: ParserLimits) -> ParseResult: ...


class IngestionIssue(d.Record):
    code: str = Field(min_length=1)
    artifact_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    severity: Literal["error", "warning"]


class IngestionReport(d.Artifact):
    status: Literal["COMPLETE", "PARTIAL", "INVALID"]
    inventory: InventoryReport
    ledger: d.SourceLedger
    parses: list[ParseResult]
    build: ProjectBuild
    validation_issues: list[IngestionIssue]
    network_used: Literal[False] = False
    external_writes: Literal[False] = False


def _parse_all(
    root: Path, report: InventoryReport, parser_limits: ParserLimits
) -> list[ParseResult]:
    return [
        parse_entry(root, entry, limits=parser_limits)
        for entry in report.entries
        if entry.entry_kind == "file" and entry.state != "IGNORED"
    ]


def _apply_parse_states(ledger: d.SourceLedger, parses: Iterable[ParseResult]) -> None:
    parsed = {result.source.id: result for result in parses}
    for source in ledger.sources:
        result = parsed.get(source.id)
        if result is None or not source.in_scope:
            continue
        source.extraction = d.Extraction(method=result.parser, version=PARSER_VERSION)
        if result.status == "PARSED":
            source.study_status = "STUDIED"
            source.read_integrity = "COMPLETE"
            source.reason = None
        elif result.status == "PARTIAL":
            source.study_status = "PARTIALLY_STUDIED"
            source.read_integrity = "PARTIAL"
            source.reason = "Parser completed with explicit unresolved limitations."
        elif result.status == "UNSUPPORTED":
            source.study_status = "NOT_STUDIED"
            source.read_integrity = "NOT_APPLICABLE"
            source.reason = "No bounded M1 parser supports this source type."
        elif result.status == "MUTATED":
            source.study_status = "BLOCKED"
            source.read_integrity = "FAILED"
            source.reason = "Source changed between inventory and parsing."
        else:
            source.study_status = "BLOCKED"
            source.read_integrity = "FAILED"
            source.reason = "Bounded parsing failed."


def _set_completeness(ledger: d.SourceLedger, *, semantic_partial: bool) -> None:
    if not ledger.manifest.inventory_complete:
        ledger.manifest.completeness = "INVALID"
        return
    incomplete = semantic_partial or any(
        source.required
        and source.in_scope
        and (source.study_status != "STUDIED" or source.read_integrity != "COMPLETE")
        for source in ledger.sources
    )
    ledger.manifest.completeness = "PARTIAL" if incomplete else "SCOPED_COMPLETE"


def ingest_local(
    root: Path,
    *,
    project_id: str,
    snapshot_id: str,
    collected_at: str,
    includes: Iterable[str] = ("*",),
    excludes: Iterable[str] = (),
    inventory_limits: InventoryLimits | None = None,
    parser_limits: ParserLimits | None = None,
    authority_class: Literal[
        "CONTRACT",
        "TECHNICAL_CONTRACT",
        "ORGANIZATIONAL_POLICY",
        "IMPLEMENTATION",
        "HISTORICAL",
        "GUIDANCE",
    ] = "GUIDANCE",
    lifecycle: Literal[
        "draft", "approved", "active", "superseded", "deprecated", "archived", "unknown"
    ] = "active",
) -> IngestionReport:
    """Run local inventory, parsing, normalization and M0 integrity validation."""

    inventory = inventory_sources(
        root,
        project_id=project_id,
        snapshot_id=snapshot_id,
        includes=includes,
        excludes=excludes,
        limits=inventory_limits,
    )
    ledger = ledger_from_inventory(
        inventory,
        collected_at=collected_at,
        authority_class=authority_class,
        lifecycle=lifecycle,
    )
    parses = _parse_all(root, inventory, parser_limits or ParserLimits())
    _apply_parse_states(ledger, parses)
    _set_completeness(ledger, semantic_partial=False)
    build = build_project_model(ledger, parses)
    semantic_errors = [issue for issue in build.issues if issue.severity == "error"]
    if semantic_errors:
        affected_sources = {issue.source.id for issue in semantic_errors}
        for source in ledger.sources:
            if source.id in affected_sources and source.study_status == "STUDIED":
                source.study_status = "PARTIALLY_STUDIED"
                source.read_integrity = "PARTIAL"
                source.reason = "Semantic normalization reported explicit limitations."
        _set_completeness(ledger, semantic_partial=True)
        build.model.ledger = ledger
    validation = validate_project_model(build.model)
    validation_issues = [
        IngestionIssue(
            code=issue.code,
            artifact_id=issue.artifact_id,
            message=issue.message,
            severity=issue.severity,
        )
        for issue in validation.issues
    ]
    if any(issue.severity == "error" for issue in validation_issues):
        status: Literal["COMPLETE", "PARTIAL", "INVALID"] = "INVALID"
    elif ledger.manifest.completeness in {"COMPLETE", "SCOPED_COMPLETE"} and not build.issues:
        status = "COMPLETE"
    else:
        status = "PARTIAL"
    return IngestionReport(
        id="ingestion-report",
        project_id=project_id,
        snapshot_id=snapshot_id,
        status=status,
        inventory=inventory,
        ledger=ledger,
        parses=parses,
        build=build,
        validation_issues=validation_issues,
    )
