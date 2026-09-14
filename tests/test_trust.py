import pytest

from qe_skill.domain import Approval, Proposal
from qe_skill.validation import (
    TrustContext,
    digest,
    validate_approval,
    validate_claim,
    validate_ledger,
    validate_oracle,
)
from tests.helpers import claim_copy, minimal, ref, reference


def test_valid_minimal_chain() -> None:
    model = minimal()
    assert validate_ledger(model.ledger).valid
    assert validate_claim(model.claims[0], model).valid
    assert validate_oracle(model.oracles[0], model).valid


@pytest.mark.parametrize("status", ["BLOCKED", "NOT_STUDIED", "PARTIALLY_STUDIED", "SUPERSEDED"])
def test_incomplete_study_cannot_claim_complete(status: str) -> None:
    model = minimal()
    source = model.ledger.sources[0]
    source.study_status = status
    source.reason = "Synthetic unavailable evidence"
    assert "SRC_FALSE_COMPLETE" in {i.code for i in validate_ledger(model.ledger).issues}
    model.ledger.manifest.completeness = "PARTIAL"
    assert validate_ledger(model.ledger).valid
    assert not validate_oracle(model.oracles[0], model).valid


@pytest.mark.parametrize(
    "integrity", ["PARTIAL", "TRUNCATED", "FAILED", "UNVERIFIED", "NOT_APPLICABLE"]
)
def test_bad_read_cannot_be_studied_or_complete(integrity: str) -> None:
    model = minimal()
    model.ledger.sources[0].read_integrity = integrity
    codes = {i.code for i in validate_ledger(model.ledger).issues}
    assert {"SRC_FALSE_COMPLETE", "SRC_STUDY_INTEGRITY"} <= codes


def test_missing_source_and_silent_scope_reduction() -> None:
    model = minimal()
    model.ledger.sources[0].required = False
    assert not validate_ledger(model.ledger).valid
    model.ledger.sources.clear()
    assert not validate_ledger(model.ledger).valid
    assert not validate_oracle(model.oracles[0], model).valid


@pytest.mark.parametrize("mutation", ["delete", "hash", "summary", "superseded", "authority"])
def test_invalid_evidence_invalidates_oracle(mutation: str) -> None:
    model = minimal()
    source = model.ledger.sources[0]
    if mutation == "delete":
        model.ledger.sources.clear()
    elif mutation == "hash":
        source.content_hash = "b" * 64
    elif mutation == "summary":
        source.primary = False
    elif mutation == "superseded":
        source.lifecycle = "superseded"
    else:
        source.authority_class = "IMPLEMENTATION"
    assert not validate_oracle(model.oracles[0], model).valid


def test_inference_and_origin_cannot_be_laundered() -> None:
    model = minimal()
    model.claims[0].inferred = True
    assert not validate_oracle(model.oracles[0], model).valid
    model.oracles[0].inferred = True
    assert not validate_oracle(model.oracles[0], model).valid
    model.claims[0].origin = "IMPLEMENTATION"
    assert "ORACLE_ORIGIN_LEAKAGE" in {
        i.code for i in validate_oracle(model.oracles[0], model).issues
    }


def test_derived_claim_cannot_hide_mutation_or_cycle() -> None:
    model = minimal()
    child = claim_copy(model, "child")
    child.derived_from = [reference("claim")]
    model.claims.append(child)
    model.oracles[0].claim = reference("child")
    model.claims[0].evidence[0].source_hash = "b" * 64
    assert not validate_oracle(model.oracles[0], model).valid
    model.claims[0].derived_from = [reference("child")]
    assert "PROV_CYCLE" in {i.code for i in validate_oracle(model.oracles[0], model).issues}


def approved_promotion():
    model = minimal()
    oracle = model.oracles[0]
    oracle.inferred = True
    oracle.approval_id = "approval"
    model.claims[0].inferred = True
    proposal = Proposal.model_validate(
        {
            **ref("proposal"),
            "preview_hash": "c" * 64,
            "source_snapshot": "v1",
            "target_snapshot": "v1",
            "operations": [
                {
                    "id": "promote",
                    "kind": "promote_oracle",
                    "target": "oracle",
                    "target_version": "v1",
                    "artifact": ref("oracle"),
                    "artifact_hash": digest(oracle),
                    "payload_hash": digest(oracle),
                    "preserve_history": True,
                    "idempotency_key": "synthetic-promotion-1",
                }
            ],
        }
    )
    approval = Approval.model_validate(
        {
            **ref("approval"),
            "actor": "synthetic-reviewer",
            "authority": "synthetic-owner",
            "timestamp": "2026-01-01T00:00:00Z",
            "decision": "APPROVED",
            "reason": "Synthetic review",
            "proposal_id": "proposal",
            "proposal_hash": digest(proposal),
            "source_snapshot": "v1",
            "target_snapshot": "v1",
            "operation_ids": ["promote"],
        }
    )
    model.proposals = [proposal]
    model.approvals = [approval]
    return model, TrustContext(frozenset({digest(approval)}))


def test_approval_requires_separate_trust_and_exact_content() -> None:
    model, context = approved_promotion()
    assert validate_oracle(model.oracles[0], model, context).valid
    assert not validate_oracle(model.oracles[0], model).valid
    model.oracles[0].statement = "Different expectation"
    assert not validate_oracle(model.oracles[0], model, context).valid


@pytest.mark.parametrize("mutation", ["snapshot", "operation", "actor", "target", "preview"])
def test_approval_mutation_rejected(mutation: str) -> None:
    model, context = approved_promotion()
    approval, proposal = model.approvals[0], model.proposals[0]
    if mutation == "snapshot":
        approval.target_snapshot = "v2"
    elif mutation == "operation":
        approval.operation_ids = ["different"]
    elif mutation == "actor":
        approval.actor = "model-self-approval"
    elif mutation == "preview":
        proposal.preview_hash = "d" * 64
    else:
        proposal.operations[0].target_version = "v2"
    assert not validate_approval(approval, proposal, context, "v1", "v1").valid


def test_cross_snapshot_and_unsupported_statement() -> None:
    model = minimal()
    model.oracles[0].claim.snapshot_id = "old"
    assert not validate_oracle(model.oracles[0], model).valid
    model.oracles[0].claim.snapshot_id = "v1"
    model.oracles[0].statement = "A fabricated exact message"
    assert not validate_oracle(model.oracles[0], model).valid
