import hashlib
import os
from pathlib import Path

import pytest

from qe_skill.inventory import (
    InventoryLimits,
    compare_inventories,
    inventory_sources,
    ledger_from_inventory,
)
from qe_skill.validation import validate_ledger


def run_inventory(root: Path, snapshot: str = "v1", **kwargs: object):
    return inventory_sources(
        root,
        project_id="synthetic",
        snapshot_id=snapshot,
        **kwargs,  # type: ignore[arg-type]
    )


def test_inventory_is_sorted_stable_and_hashes_exact_bytes(tmp_path: Path) -> None:
    (tmp_path / "z.txt").write_text("last", encoding="utf-8")
    (tmp_path / "A.md").write_text("first", encoding="utf-8")
    first = run_inventory(tmp_path)
    second = run_inventory(tmp_path)
    assert [item.path for item in first.entries] == ["A.md", "z.txt"]
    assert first.model_dump() == second.model_dump()
    assert first.entries[0].content_hash == hashlib.sha256(b"first").hexdigest()


def test_mutation_and_deletion_are_visible(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    removed = tmp_path / "removed.json"
    source.write_text("before", encoding="utf-8")
    removed.write_text("{}", encoding="utf-8")
    before = run_inventory(tmp_path)
    source.write_text("after", encoding="utf-8")
    removed.unlink()
    after = run_inventory(tmp_path, "v2")
    assert [(change.path, change.change) for change in compare_inventories(before, after)] == [
        ("removed.json", "DELETED"),
        ("source.txt", "MUTATED"),
    ]


def test_empty_nested_unicode_and_default_ignored_directories(tmp_path: Path) -> None:
    assert run_inventory(tmp_path).entries == []
    nested = tmp_path / "área" / "deeper"
    nested.mkdir(parents=True)
    (nested / "evidence ü.md").write_text("# Evidence", encoding="utf-8")
    ignored = tmp_path / ".venv"
    ignored.mkdir()
    (ignored / "not-evidence.py").write_text("raise SystemExit", encoding="utf-8")
    report = run_inventory(tmp_path)
    assert [item.path for item in report.entries] == ["área/deeper/evidence ü.md"]
    assert report.ignored_directories == [".venv"]


def test_include_exclude_unsupported_and_oversized_states(tmp_path: Path) -> None:
    (tmp_path / "keep.md").write_text("kept", encoding="utf-8")
    (tmp_path / "skip.md").write_text("skipped", encoding="utf-8")
    (tmp_path / "binary.zip").write_bytes(b"PK synthetic")
    (tmp_path / "large.txt").write_text("12345", encoding="utf-8")
    report = run_inventory(
        tmp_path,
        excludes=("skip.md",),
        limits=InventoryLimits(max_file_bytes=4),
    )
    states = {item.path: item.state for item in report.entries}
    assert states == {
        "binary.zip": "LIMIT_EXCEEDED",
        "keep.md": "INVENTORIED",
        "large.txt": "LIMIT_EXCEEDED",
        "skip.md": "IGNORED",
    }
    unsupported = run_inventory(tmp_path, includes=("*.zip",))
    assert {item.path: item.state for item in unsupported.entries}["binary.zip"] == "UNSUPPORTED"


def test_file_count_and_depth_limits_are_explicit(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_text("a", encoding="utf-8")
    (tmp_path / "b.txt").write_text("b", encoding="utf-8")
    deep = tmp_path / "one"
    deep.mkdir()
    (deep / "nested.txt").write_text("nested", encoding="utf-8")
    report = run_inventory(tmp_path, limits=InventoryLimits(max_files=1, max_depth=0))
    assert not report.inventory_complete
    assert any(item.state == "LIMIT_EXCEEDED" for item in report.entries)
    assert any("depth limit" in issue.lower() for issue in report.issues)


def test_unreadable_file_is_reported(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    source = tmp_path / "blocked.txt"
    source.write_text("synthetic", encoding="utf-8")
    original = Path.read_bytes

    def blocked(path: Path) -> bytes:
        if path.name == "blocked.txt":
            raise PermissionError("synthetic denied")
        return original(path)

    monkeypatch.setattr(Path, "read_bytes", blocked)
    entry = run_inventory(tmp_path).entries[0]
    assert entry.state == "UNREADABLE"
    assert entry.content_hash is None


def test_internal_file_symlink_and_escape_are_explicit(tmp_path: Path) -> None:
    target = tmp_path / "target.txt"
    target.write_text("inside", encoding="utf-8")
    internal = tmp_path / "internal.txt"
    external_target = tmp_path.parent / f"outside-{os.getpid()}.txt"
    external = tmp_path / "external.txt"
    external_target.write_text("outside", encoding="utf-8")
    try:
        try:
            internal.symlink_to(target)
            external.symlink_to(external_target)
        except OSError:
            pytest.skip("This platform does not permit test symlink creation.")
        states = {item.path: item.state for item in run_inventory(tmp_path).entries}
        assert states["internal.txt"] == "INVENTORIED"
        assert states["external.txt"] == "SYMLINK_ESCAPES_ROOT"
    finally:
        external_target.unlink(missing_ok=True)


def test_ledger_bridge_never_calls_inventory_studied(tmp_path: Path) -> None:
    (tmp_path / "evidence.md").write_text("# Evidence", encoding="utf-8")
    report = run_inventory(tmp_path)
    ledger = ledger_from_inventory(report, collected_at="2026-01-01T00:00:00Z")
    assert ledger.sources[0].study_status == "NOT_STUDIED"
    assert ledger.sources[0].read_integrity == "UNVERIFIED"
    assert ledger.manifest.completeness == "PARTIAL"
    assert validate_ledger(ledger).valid
