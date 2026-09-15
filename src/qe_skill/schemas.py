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
from qe_skill.ingestion import IngestionReport
from qe_skill.inventory import InventoryReport
from qe_skill.m2 import (
    AuditFindings,
    CoverageReport,
    M2AnalysisReport,
    ProposalSet,
    RiskAnalysis,
    ScenarioUniverse,
    TraceabilityGraph,
)
from qe_skill.m3 import (
    GeneratedCaseProposal,
    GenerationManifest,
    GenerationTraceabilityEdge,
    M3GenerationReport,
    ParameterCandidate,
    SharedStepCandidate,
    TestRevisionProposal,
)
from qe_skill.parsers import ParseResult
from qe_skill.project_builder import ProjectBuild
from qe_skill.reasoning import ReasoningRequest, ReasoningResult
from qe_skill.semantic import SemanticCacheBinding, SemanticCandidate, SemanticCandidateSet

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
    "source-extraction": ParseResult,
    "project-build": ProjectBuild,
    "ingestion-report": IngestionReport,
    "m2-analysis-report": M2AnalysisReport,
    "traceability": TraceabilityGraph,
    "coverage-report": CoverageReport,
    "audit-findings": AuditFindings,
    "risk-analysis": RiskAnalysis,
    "scenario-universe": ScenarioUniverse,
    "m2-proposals": ProposalSet,
    "m3-generation-report": M3GenerationReport,
    "generated-case-proposal": GeneratedCaseProposal,
    "test-revision-proposal": TestRevisionProposal,
    "shared-step-candidate": SharedStepCandidate,
    "parameter-candidate": ParameterCandidate,
    "generation-traceability": GenerationTraceabilityEdge,
    "generation-manifest": GenerationManifest,
    "reasoning-request": ReasoningRequest,
    "reasoning-result": ReasoningResult,
    "semantic-candidate": SemanticCandidate,
    "semantic-candidate-set": SemanticCandidateSet,
    "semantic-cache-binding": SemanticCacheBinding,
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
