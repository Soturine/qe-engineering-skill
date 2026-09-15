"""Reproducible Draft 2020-12 schema exports from the versioned contracts."""

import json
from pathlib import Path

from pydantic import BaseModel

from qe_skill.domain import (
    Approval,
    Claim,
    Oracle,
    ProjectModel,
    Proposal,
    Risk,
    RunManifest,
    SourceLedger,
    TestCase,
    TestModel,
)
from qe_skill.inventory import InventoryReport

CONTRACTS: dict[str, type[BaseModel]] = {
    "run-manifest": RunManifest,
    "source-ledger": SourceLedger,
    "claim-provenance": Claim,
    "oracle": Oracle,
    "approval": Approval,
    "proposal": Proposal,
    "risk": Risk,
    "project-model": ProjectModel,
    "test-case": TestCase,
    "test-model": TestModel,
    "source-inventory": InventoryReport,
}


def schema_text(name: str) -> str:
    schema = CONTRACTS[name].model_json_schema()
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"urn:qe-skill:1.0:{name}"
    return json.dumps(schema, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def export(directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name in CONTRACTS:
        (directory / f"{name}.schema.json").write_text(schema_text(name), encoding="utf-8")


if __name__ == "__main__":
    export(Path("schemas/v1"))
