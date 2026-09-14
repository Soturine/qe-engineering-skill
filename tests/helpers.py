"""Synthetic evidence builders; no real project behavior or source content."""

from qe_skill.domain import Claim, ProjectModel, Ref


def ref(identifier: str) -> dict[str, str]:
    return {"id": identifier, "project_id": "synthetic", "snapshot_id": "v1"}


def minimal() -> ProjectModel:
    return ProjectModel.model_validate(
        {
            **ref("model"),
            "ledger": {
                **ref("ledger"),
                "manifest": {
                    **ref("run"),
                    "mode": "GREENFIELD",
                    "scope_description": "Synthetic contract",
                    "scope": [{"source": ref("source"), "required": True, "in_scope": True}],
                    "containers": ["synthetic-contract"],
                    "inventory_complete": True,
                    "completeness": "COMPLETE",
                    "created_at": "2026-01-01T00:00:00Z",
                    "tool_version": "synthetic-1",
                    "authority_policy": "approved-contract-only",
                },
                "sources": [
                    {
                        **ref("source"),
                        "source_type": "specification",
                        "locator": "synthetic://contract",
                        "version": "1",
                        "content_hash": "a" * 64,
                        "collected_at": "2026-01-01T00:00:00Z",
                        "authority_class": "CONTRACT",
                        "lifecycle": "approved",
                        "study_status": "STUDIED",
                        "read_integrity": "COMPLETE",
                        "required": True,
                        "in_scope": True,
                        "primary": True,
                        "extraction": {"method": "synthetic", "version": "1"},
                        "sensitivity": "public-synthetic",
                        "handling": "local",
                    }
                ],
            },
            "claims": [
                {
                    **ref("claim"),
                    "statement": "The synthetic record is retained.",
                    "origin": "CONTRACT",
                    "evidence": [
                        {"source": ref("source"), "source_hash": "a" * 64, "location": "clause 1"}
                    ],
                    "inferred": False,
                    "confidence": 1.0,
                    "conflict": "none",
                    "extraction": {"method": "synthetic", "version": "1"},
                }
            ],
            "oracles": [
                {
                    **ref("oracle"),
                    "statement": "The synthetic record is retained.",
                    "origin": "CONTRACT",
                    "claim": ref("claim"),
                    "normative": True,
                    "inferred": False,
                    "confidence": 1.0,
                    "usage": "acceptance",
                }
            ],
            "nodes": [],
            "tests": {**ref("tests"), "test_cases": [], "proposal_only": True},
        }
    )


def claim_copy(model: ProjectModel, identifier: str) -> Claim:
    claim = model.claims[0].model_copy(deep=True)
    claim.id = identifier
    return claim


def reference(identifier: str) -> Ref:
    return Ref.model_validate(ref(identifier))
