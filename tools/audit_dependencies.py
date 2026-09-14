"""Fail on published PyPI advisories or unavailable audit metadata. No project data sent."""

import json
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


def pins(path: Path) -> list[tuple[str, str]]:
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)==([A-Za-z0-9_.+-]+)", line)
        if match is None:
            raise ValueError("Audit requires exact public package/version pins.")
        result.append((match[1], match[2]))
    if not result:
        raise ValueError("Dependency lock is empty.")
    return result


def advisory_ids(metadata: object) -> list[str]:
    if not isinstance(metadata, dict) or not isinstance(metadata.get("vulnerabilities"), list):
        raise ValueError("Registry response lacks advisory metadata.")
    findings = []
    for advisory in metadata["vulnerabilities"]:
        if not isinstance(advisory, dict) or not isinstance(advisory.get("id"), str):
            raise ValueError("Registry advisory metadata is malformed.")
        if not advisory.get("withdrawn"):
            findings.append(advisory["id"])
    return findings


def main() -> int:
    findings = {}
    try:
        dependencies = pins(Path("requirements-dev.lock"))
        for name, version in dependencies:
            with urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=20) as response:
                metadata = json.load(response)
            advisories = advisory_ids(metadata)
            if advisories:
                findings[f"{name}=={version}"] = advisories
    except (OSError, ValueError, URLError):
        print("Dependency audit unavailable or malformed; no clean-audit claim.")
        return 1
    print(
        json.dumps(
            {
                "registry": "PyPI published advisories",
                "packages": len(dependencies),
                "findings": findings,
            },
            sort_keys=True,
        )
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
