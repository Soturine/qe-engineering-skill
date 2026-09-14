import tomllib
from importlib.metadata import requires
from pathlib import Path

import pytest
from packaging.requirements import Requirement

from tools.audit_dependencies import advisory_ids, pins


def normalize(name: str) -> str:
    return name.lower().replace("_", "-")


def test_direct_and_build_dependencies_match_lock() -> None:
    project = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    lock = {normalize(name): version for name, version in pins(Path("requirements-dev.lock"))}
    dependencies = (
        project["project"]["dependencies"]
        + project["project"]["optional-dependencies"]["dev"]
        + project["build-system"]["requires"]
    )
    for dependency in dependencies:
        name, version = dependency.split("==")
        assert lock[normalize(name)] == version


def test_advisory_audit_does_not_hide_unknown_or_active_findings() -> None:
    with pytest.raises(ValueError):
        advisory_ids({})
    assert advisory_ids({"vulnerabilities": [{"id": "SYNTHETIC-ADVISORY", "withdrawn": None}]})
    assert not advisory_ids({"vulnerabilities": [{"id": "WITHDRAWN", "withdrawn": "synthetic"}]})


def test_transitive_dependencies_are_also_locked() -> None:
    lock = {normalize(name): version for name, version in pins(Path("requirements-dev.lock"))}
    for name in lock:
        for text in requires(name) or []:
            requirement = Requirement(text)
            if requirement.marker is None or requirement.marker.evaluate({"extra": ""}):
                dependency = normalize(requirement.name)
                assert dependency in lock, (name, dependency)
                assert lock[dependency] in requirement.specifier
