"""Deterministic, bounded local source inventory and M0 ledger population."""

from __future__ import annotations

import fnmatch
import hashlib
import os
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from pydantic import Field

from qe_skill import __version__
from qe_skill.domain import (
    Artifact,
    Digest,
    Extraction,
    Ref,
    RunManifest,
    ScopeEntry,
    Source,
    SourceLedger,
)

DEFAULT_IGNORED_DIRECTORIES = frozenset(
    {
        ".git",
        ".hg",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".svn",
        ".tox",
        ".venv",
        "__pycache__",
        "build",
        "dist",
        "node_modules",
    }
)
SUPPORTED_EXTENSIONS = frozenset({".json", ".md", ".markdown", ".py", ".txt", ".yaml", ".yml"})


@dataclass(frozen=True)
class InventoryLimits:
    max_files: int = 10_000
    max_file_bytes: int = 2 * 1024 * 1024
    max_depth: int = 32

    def __post_init__(self) -> None:
        if self.max_files < 1 or self.max_file_bytes < 1 or self.max_depth < 0:
            raise ValueError("Inventory limits must be positive (depth may be zero).")


class InventoryEntry(Artifact):
    path: str = Field(min_length=1)
    entry_kind: Literal["file", "directory", "symlink"]
    extension: str
    source_type: str = Field(min_length=1)
    size_bytes: int | None = Field(default=None, ge=0)
    modified_ns: int | None = Field(default=None, ge=0)
    content_hash: Digest | None = None
    state: Literal[
        "INVENTORIED",
        "IGNORED",
        "UNSUPPORTED",
        "UNREADABLE",
        "LIMIT_EXCEEDED",
        "SYMLINK_ESCAPES_ROOT",
    ]
    reason: str | None = None
    symlink: bool = False


class InventoryReport(Artifact):
    root: str = Field(min_length=1)
    includes: list[str]
    excludes: list[str]
    limits: dict[str, int]
    entries: list[InventoryEntry]
    ignored_directories: list[str]
    inventory_complete: bool
    issues: list[str]


class InventoryChange(Artifact):
    path: str = Field(min_length=1)
    change: Literal["ADDED", "DELETED", "MUTATED", "STATE_CHANGED"]
    before_hash: Digest | None = None
    after_hash: Digest | None = None
    before_state: str | None = None
    after_state: str | None = None


def _source_type(extension: str) -> str:
    return {
        ".json": "json",
        ".md": "markdown",
        ".markdown": "markdown",
        ".py": "python",
        ".txt": "text",
        ".yaml": "yaml",
        ".yml": "yaml",
    }.get(extension, "unsupported")


def _identifier(project_id: str, snapshot_id: str, relative_path: str) -> str:
    value = f"{project_id}\0{snapshot_id}\0{relative_path}".encode()
    return f"source.{hashlib.sha256(value).hexdigest()[:24]}"


def _matches(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns)


def _inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.relative_to(root)
    except ValueError:
        return False
    return True


def inventory_sources(
    root: Path,
    *,
    project_id: str,
    snapshot_id: str,
    includes: Iterable[str] = ("*",),
    excludes: Iterable[str] = (),
    limits: InventoryLimits | None = None,
    follow_internal_file_symlinks: bool = True,
) -> InventoryReport:
    """Inventory an explicit directory without executing or importing its content."""

    resolved_root = root.resolve(strict=True)
    if not resolved_root.is_dir():
        raise ValueError("Inventory root must be an existing directory.")
    include_patterns = tuple(includes)
    exclude_patterns = tuple(excludes)
    limits = limits or InventoryLimits()
    if not include_patterns or any(not pattern for pattern in include_patterns + exclude_patterns):
        raise ValueError("Include patterns must be non-empty and all patterns must contain text.")

    entries: list[InventoryEntry] = []
    ignored_directories: list[str] = []
    issues: list[str] = []
    inventory_complete = True
    file_count = 0

    def make_entry(relative: str, **values: object) -> InventoryEntry:
        return InventoryEntry.model_validate(
            {
                "id": _identifier(project_id, snapshot_id, relative),
                "project_id": project_id,
                "snapshot_id": snapshot_id,
                "path": relative,
                **values,
            }
        )

    def walk(directory: Path, relative_directory: str, depth: int) -> None:
        nonlocal file_count, inventory_complete
        try:
            children = sorted(
                os.scandir(directory), key=lambda item: (item.name.casefold(), item.name)
            )
        except OSError:
            inventory_complete = False
            location = relative_directory or "."
            issues.append(f"Directory could not be read: {location}")
            entries.append(
                make_entry(
                    location,
                    entry_kind="directory",
                    extension="",
                    source_type="directory",
                    state="UNREADABLE",
                    reason="Directory could not be read.",
                )
            )
            return
        for child in children:
            relative = f"{relative_directory}/{child.name}" if relative_directory else child.name
            relative = relative.replace("\\", "/")
            if child.is_symlink():
                try:
                    target = Path(child.path).resolve(strict=True)
                except OSError:
                    inventory_complete = False
                    entries.append(
                        make_entry(
                            relative,
                            entry_kind="symlink",
                            extension=Path(child.name).suffix.lower(),
                            source_type="symlink",
                            state="UNREADABLE",
                            reason="Symlink target could not be resolved.",
                            symlink=True,
                        )
                    )
                    continue
                if not _inside(resolved_root, target):
                    inventory_complete = False
                    entries.append(
                        make_entry(
                            relative,
                            entry_kind="symlink",
                            extension=Path(child.name).suffix.lower(),
                            source_type="symlink",
                            state="SYMLINK_ESCAPES_ROOT",
                            reason="Symlink target is outside the configured root.",
                            symlink=True,
                        )
                    )
                    continue
                if target.is_dir() or not follow_internal_file_symlinks:
                    entries.append(
                        make_entry(
                            relative,
                            entry_kind="symlink",
                            extension=Path(child.name).suffix.lower(),
                            source_type="symlink",
                            state="UNSUPPORTED",
                            reason="Directory symlinks are not followed."
                            if target.is_dir()
                            else "Following file symlinks is disabled.",
                            symlink=True,
                        )
                    )
                    continue
                process_file(target, relative, symlink=True)
                continue
            if child.is_dir(follow_symlinks=False):
                if child.name in DEFAULT_IGNORED_DIRECTORIES or _matches(
                    relative, exclude_patterns
                ):
                    ignored_directories.append(relative)
                    continue
                if depth >= limits.max_depth:
                    inventory_complete = False
                    entries.append(
                        make_entry(
                            relative,
                            entry_kind="directory",
                            extension="",
                            source_type="directory",
                            state="LIMIT_EXCEEDED",
                            reason="Traversal depth limit reached; directory was not entered.",
                        )
                    )
                    issues.append(f"Traversal depth limit reached: {relative}")
                    continue
                walk(Path(child.path), relative, depth + 1)
                continue
            if child.is_file(follow_symlinks=False):
                process_file(Path(child.path), relative, symlink=False)

    def process_file(path: Path, relative: str, *, symlink: bool) -> None:
        nonlocal file_count, inventory_complete
        file_count += 1
        extension = Path(relative).suffix.lower()
        common = {
            "entry_kind": "file",
            "extension": extension,
            "source_type": _source_type(extension),
            "symlink": symlink,
        }
        if file_count > limits.max_files:
            inventory_complete = False
            entries.append(
                make_entry(
                    relative,
                    **common,
                    state="LIMIT_EXCEEDED",
                    reason="File-count limit exceeded; content was not read.",
                )
            )
            issues.append(f"File-count limit exceeded at: {relative}")
            return
        if _matches(relative, exclude_patterns) or not _matches(relative, include_patterns):
            entries.append(
                make_entry(
                    relative,
                    **common,
                    state="IGNORED",
                    reason="Path does not match configured include/exclude scope.",
                )
            )
            return
        try:
            before = path.stat()
            if before.st_size > limits.max_file_bytes:
                entries.append(
                    make_entry(
                        relative,
                        **common,
                        size_bytes=before.st_size,
                        modified_ns=before.st_mtime_ns,
                        state="LIMIT_EXCEEDED",
                        reason="File exceeds the configured byte limit; content was not read.",
                    )
                )
                return
            data = path.read_bytes()
            after = path.stat()
        except OSError:
            entries.append(
                make_entry(
                    relative,
                    **common,
                    state="UNREADABLE",
                    reason="File metadata or content could not be read.",
                )
            )
            return
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            inventory_complete = False
            entries.append(
                make_entry(
                    relative,
                    **common,
                    size_bytes=after.st_size,
                    modified_ns=after.st_mtime_ns,
                    state="UNREADABLE",
                    reason="File mutated while it was being inventoried.",
                )
            )
            return
        state = "INVENTORIED" if extension in SUPPORTED_EXTENSIONS else "UNSUPPORTED"
        entries.append(
            make_entry(
                relative,
                **common,
                size_bytes=len(data),
                modified_ns=after.st_mtime_ns,
                content_hash=hashlib.sha256(data).hexdigest(),
                state=state,
                reason=None if state == "INVENTORIED" else "No M1 semantic parser for this type.",
            )
        )

    walk(resolved_root, "", 0)
    entries.sort(key=lambda item: (item.path.casefold(), item.path))
    ignored_directories.sort(key=lambda value: (value.casefold(), value))
    return InventoryReport(
        id="inventory",
        project_id=project_id,
        snapshot_id=snapshot_id,
        root=str(resolved_root),
        includes=list(include_patterns),
        excludes=list(exclude_patterns),
        limits={
            "max_files": limits.max_files,
            "max_file_bytes": limits.max_file_bytes,
            "max_depth": limits.max_depth,
        },
        entries=entries,
        ignored_directories=ignored_directories,
        inventory_complete=inventory_complete,
        issues=issues,
    )


def ledger_from_inventory(
    report: InventoryReport,
    *,
    collected_at: str,
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
    ] = "unknown",
) -> SourceLedger:
    """Bridge inventoried file states into the existing M0 Source Ledger contract."""

    sources: list[Source] = []
    scope: list[ScopeEntry] = []
    for entry in report.entries:
        if entry.entry_kind != "file":
            continue
        in_scope = entry.state != "IGNORED"
        required = in_scope
        integrity: Literal["UNVERIFIED", "FAILED", "NOT_APPLICABLE"]
        if entry.state in {"UNREADABLE", "LIMIT_EXCEEDED"}:
            integrity = "FAILED"
        elif entry.state in {"UNSUPPORTED", "SYMLINK_ESCAPES_ROOT", "IGNORED"}:
            integrity = "NOT_APPLICABLE"
        else:
            integrity = "UNVERIFIED"
        reason = entry.reason or "Inventoried only; semantic parsing has not run."
        source = Source(
            id=entry.id,
            project_id=report.project_id,
            snapshot_id=report.snapshot_id,
            source_type=entry.source_type,
            locator=entry.path,
            version=None,
            content_hash=entry.content_hash,
            hash_unavailable_reason=None
            if entry.content_hash is not None
            else "Content was not safely readable within configured limits.",
            collected_at=collected_at,
            authority_class=authority_class,
            lifecycle=lifecycle,
            study_status="OUT_OF_SCOPE" if not in_scope else "NOT_STUDIED",
            read_integrity=integrity,
            required=required,
            in_scope=in_scope,
            reason=reason,
            primary=True,
            extraction=Extraction(method="deterministic-inventory", version="1.0"),
            sensitivity="unclassified",
            handling="local-bounded-read",
        )
        sources.append(source)
        scope.append(
            ScopeEntry(
                source=source_ref(source),
                required=required,
                in_scope=in_scope,
                decision_reason=entry.reason if not in_scope else None,
            )
        )
    completeness: Literal["PARTIAL", "INVALID"] = (
        "PARTIAL" if report.inventory_complete else "INVALID"
    )
    manifest = RunManifest(
        id="run",
        project_id=report.project_id,
        snapshot_id=report.snapshot_id,
        mode="GREENFIELD",
        scope_description=f"Explicit local source scope rooted at {report.root}",
        scope=scope,
        containers=[report.root],
        inventory_complete=report.inventory_complete,
        completeness=completeness,
        created_at=collected_at,
        tool_version=__version__,
        authority_policy="Operator must classify source authority; inventory defaults to GUIDANCE.",
    )
    return SourceLedger(
        id="ledger",
        project_id=report.project_id,
        snapshot_id=report.snapshot_id,
        manifest=manifest,
        sources=sources,
    )


def compare_inventories(before: InventoryReport, after: InventoryReport) -> list[InventoryChange]:
    """Expose additions, deletions, byte mutations and state changes between snapshots."""

    if before.project_id != after.project_id:
        raise ValueError("Inventories from different projects cannot be compared.")
    previous = {entry.path: entry for entry in before.entries}
    current = {entry.path: entry for entry in after.entries}
    changes: list[InventoryChange] = []
    for path in sorted(
        previous.keys() | current.keys(), key=lambda value: (value.casefold(), value)
    ):
        old = previous.get(path)
        new = current.get(path)
        if old is None and new is not None:
            kind: Literal["ADDED", "DELETED", "MUTATED", "STATE_CHANGED"] = "ADDED"
        elif old is not None and new is None:
            kind = "DELETED"
        elif old is not None and new is not None and old.content_hash != new.content_hash:
            kind = "MUTATED"
        elif old is not None and new is not None and old.state != new.state:
            kind = "STATE_CHANGED"
        else:
            continue
        changes.append(
            InventoryChange(
                id=f"change.{hashlib.sha256(path.encode()).hexdigest()[:24]}",
                project_id=after.project_id,
                snapshot_id=after.snapshot_id,
                path=path,
                change=kind,
                before_hash=old.content_hash if old else None,
                after_hash=new.content_hash if new else None,
                before_state=old.state if old else None,
                after_state=new.state if new else None,
            )
        )
    return changes


def source_ref(source: Source) -> Ref:
    return Ref(id=source.id, project_id=source.project_id, snapshot_id=source.snapshot_id)
