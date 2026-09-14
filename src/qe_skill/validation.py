"""Deterministic, fail-closed checks over declared evidence, never semantic extraction."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from qe_skill.domain import (
    Approval,
    Artifact,
    Claim,
    Oracle,
    ProjectModel,
    Proposal,
    Ref,
    Source,
    SourceLedger,
)


@dataclass(frozen=True)
class Issue:
    code: str
    artifact_id: str
    message: str
    severity: Literal["error", "warning"] = "error"


@dataclass
class Result:
    issues: list[Issue] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return not any(issue.severity == "error" for issue in self.issues)

    def add(
        self,
        code: str,
        artifact: Artifact | str,
        message: str,
        severity: Literal["error", "warning"] = "error",
    ) -> None:
        self.issues.append(
            Issue(
                code, artifact.id if isinstance(artifact, Artifact) else artifact, message, severity
            )
        )


@dataclass(frozen=True)
class TrustContext:
    """Operator/governance input, never taken from the analyzed Project Model.

    Approval hashes attest full approval records. A caller must authenticate the
    human before admitting a hash here. M0 verifies bindings, not human identity.
    """

    approved_record_hashes: frozenset[str] = frozenset()


NO_APPROVALS = TrustContext()


def digest(record: BaseModel) -> str:
    payload = json.dumps(
        record.model_dump(mode="json"),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def same_scope(left: Artifact | Ref, right: Artifact | Ref) -> bool:
    return (left.project_id, left.snapshot_id) == (right.project_id, right.snapshot_id)


def timestamp_valid(value: str) -> bool:
    try:
        datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return False
    return True


def validate_ledger(ledger: SourceLedger) -> Result:
    result = Result()
    manifest = ledger.manifest
    if not same_scope(ledger, manifest):
        result.add("SCOPE_NAMESPACE", manifest, "Manifest and ledger namespaces differ.")
    if not timestamp_valid(manifest.created_at):
        result.add("SRC_TIMESTAMP", manifest, "Collection timestamp is not a valid UTC date.")
    sources: dict[str, Source] = {}
    for source in ledger.sources:
        if source.id in sources:
            result.add("MODEL_DUPLICATE_ID", source, "Duplicate source identifier.")
        sources[source.id] = source
        if not same_scope(source, ledger):
            result.add("SCOPE_NAMESPACE", source, "Source is outside the ledger namespace.")
        if not timestamp_valid(source.collected_at):
            result.add("SRC_TIMESTAMP", source, "Collection timestamp is not a valid UTC date.")
        if source.content_hash is None and source.hash_unavailable_reason is None:
            result.add("SRC_IDENTITY", source, "Missing content hash must have an explicit reason.")
        if source.study_status == "STUDIED" and source.read_integrity != "COMPLETE":
            result.add("SRC_STUDY_INTEGRITY", source, "Studied source must have complete reads.")
        if (source.study_status != "STUDIED" or not source.in_scope) and not source.reason:
            result.add("SRC_REASON", source, "Incomplete or excluded source needs a reason.")
        if source.study_status == "OUT_OF_SCOPE" and source.in_scope:
            result.add(
                "SRC_SCOPE_DECISION", source, "Out-of-scope status conflicts with scope flag."
            )
    scope_ids: set[str] = set()
    incomplete = not manifest.inventory_complete
    for entry in manifest.scope:
        ref = entry.source
        if ref.id in scope_ids:
            result.add("MODEL_DUPLICATE_ID", ref.id, "Duplicate configured scope source.")
        scope_ids.add(ref.id)
        if not same_scope(ref, ledger):
            result.add("SCOPE_NAMESPACE", ref.id, "Scope entry belongs to another namespace.")
        scoped_source = sources.get(ref.id)
        if scoped_source is None:
            result.add("SRC_MISSING", ref.id, "Expected source is absent from the ledger.")
            incomplete = True
            continue
        source = scoped_source
        if (entry.required, entry.in_scope) != (source.required, source.in_scope):
            result.add("SRC_SCOPE_DECISION", source, "Ledger silently changes configured scope.")
        if (not entry.required or not entry.in_scope) and not entry.decision_reason:
            result.add("SRC_SCOPE_DECISION", source, "Scope exclusion needs an explicit decision.")
        if (
            entry.required
            and entry.in_scope
            and (
                source.study_status != "STUDIED"
                or source.read_integrity != "COMPLETE"
                or source.lifecycle in {"superseded", "deprecated", "archived"}
            )
        ):
            incomplete = True
            result.add(
                "SRC_INCOMPLETE", source, "Required source is incomplete or inactive.", "warning"
            )
    for source_id in sources.keys() - scope_ids:
        result.add("SRC_UNACCOUNTED", source_id, "Discovered source is absent from declared scope.")
    if not manifest.inventory_complete:
        result.add(
            "SRC_INVENTORY_PARTIAL", manifest, "Container inventory is incomplete.", "warning"
        )
    if incomplete and manifest.completeness in {"COMPLETE", "SCOPED_COMPLETE"}:
        result.add("SRC_FALSE_COMPLETE", manifest, "Required scope does not support completeness.")
    return result


def source_usable(source: Source) -> bool:
    return (
        source.primary
        and source.in_scope
        and source.study_status == "STUDIED"
        and source.read_integrity == "COMPLETE"
        and source.lifecycle in {"active", "approved"}
        and source.content_hash is not None
    )


def validate_claim(claim: Claim, model: ProjectModel) -> Result:
    result = Result()
    if not same_scope(claim, model):
        result.add("SCOPE_NAMESPACE", claim, "Claim is outside the model namespace.")
    sources = {source.id: source for source in model.ledger.sources}
    claims = {item.id: item for item in model.claims}
    if not claim.evidence:
        result.add("PROV_MISSING", claim, "Claim has no primary evidence locations.")
    for evidence in claim.evidence:
        source = sources.get(evidence.source.id)
        if not same_scope(evidence.source, model):
            result.add("SCOPE_NAMESPACE", claim, "Evidence reference is outside the namespace.")
        if source is None:
            result.add("PROV_SOURCE_MISSING", claim, "Supporting source no longer exists.")
            continue
        if not same_scope(source, model) or not source_usable(source):
            result.add(
                "PROV_SOURCE_UNUSABLE", claim, "Evidence is not current, complete and primary."
            )
        if evidence.source_hash != source.content_hash:
            result.add(
                "PROV_SOURCE_MUTATED", claim, "Evidence digest differs from the current source."
            )
        allowed = {
            "CONTRACT": {"CONTRACT", "TECHNICAL_CONTRACT"},
            "ORGANIZATIONAL_POLICY": {"ORGANIZATIONAL_POLICY"},
        }
        if claim.origin in allowed and (
            source.authority_class not in allowed[claim.origin] or source.lifecycle != "approved"
        ):
            result.add("PROV_AUTHORITY", claim, "Source authority does not support claim origin.")
    if claim.conflict != "none":
        # A free-form 'resolved' flag is not an authority decision.
        result.add(
            "PROV_CONFLICT", claim, "Conflicted claim requires an explicit model resolution."
        )
    for parent_ref in claim.derived_from:
        parent = claims.get(parent_ref.id)
        if not same_scope(parent_ref, model):
            result.add("SCOPE_NAMESPACE", claim, "Parent claim is outside the namespace.")
        if parent is None:
            result.add("PROV_PARENT_MISSING", claim, "Derivation parent is missing.")
        elif (parent.inferred and not claim.inferred) or claim.confidence > parent.confidence:
            result.add("PROV_UNCERTAINTY", claim, "Derivation silently increases certainty.")
        elif parent.origin != claim.origin:
            result.add("PROV_AUTHORITY", claim, "Derivation silently changes origin authority.")
    pending = [ref.id for ref in claim.derived_from]
    visited: set[str] = set()
    while pending:
        current = pending.pop()
        if current == claim.id:
            result.add("PROV_CYCLE", claim, "Claim derivation contains a cycle.")
            break
        if current not in visited and current in claims:
            visited.add(current)
            pending.extend(ref.id for ref in claims[current].derived_from)
    return result


def validate_approval(
    approval: Approval,
    proposal: Proposal,
    context: TrustContext,
    source_snapshot: str,
    target_snapshot: str,
) -> Result:
    result = Result()
    if not same_scope(approval, proposal):
        result.add("SCOPE_NAMESPACE", approval, "Approval and proposal namespaces differ.")
    if digest(approval) not in context.approved_record_hashes:
        result.add(
            "APPROVAL_UNTRUSTED", approval, "Approval has no trusted governance attestation."
        )
    if approval.decision != "APPROVED" or not timestamp_valid(approval.timestamp):
        result.add(
            "APPROVAL_INVALID", approval, "Decision or timestamp does not authorize approval."
        )
    if approval.proposal_id != proposal.id or approval.proposal_hash != digest(proposal):
        result.add("APPROVAL_SCOPE", approval, "Approval does not bind the exact proposal content.")
    operations = [operation.id for operation in proposal.operations]
    if (
        len(set(operations)) != len(operations)
        or len(set(approval.operation_ids)) != len(approval.operation_ids)
        or set(approval.operation_ids) != set(operations)
    ):
        result.add(
            "APPROVAL_OPERATIONS", approval, "Approval must bind the exact unique operation set."
        )
    if (
        approval.source_snapshot != source_snapshot
        or proposal.source_snapshot != source_snapshot
        or approval.target_snapshot != target_snapshot
        or proposal.target_snapshot != target_snapshot
        or proposal.snapshot_id != source_snapshot
    ):
        result.add("APPROVAL_STALE", approval, "Source or target snapshot has changed.")
    keys: set[str] = set()
    for operation in proposal.operations:
        if not same_scope(operation.artifact, proposal):
            result.add(
                "SCOPE_NAMESPACE", proposal, "Operation artifact is outside the proposal scope."
            )
        if operation.idempotency_key in keys:
            result.add(
                "APPROVAL_IDEMPOTENCY", proposal, "Operation idempotency keys must be unique."
            )
        keys.add(operation.idempotency_key)
    return result


def oracle_approval(oracle: Oracle, model: ProjectModel, context: TrustContext) -> Result:
    result = Result()
    approval = next((a for a in model.approvals if a.id == oracle.approval_id), None)
    if approval is None:
        result.add("APPROVAL_MISSING", oracle, "Oracle promotion requires an approval record.")
        return result
    proposal = next((p for p in model.proposals if p.id == approval.proposal_id), None)
    if proposal is None:
        result.add("APPROVAL_PROPOSAL_MISSING", approval, "Approved proposal does not exist.")
        return result
    result.issues.extend(
        validate_approval(approval, proposal, context, model.snapshot_id, model.snapshot_id).issues
    )
    if len(proposal.operations) != 1:
        result.add("APPROVAL_SCOPE", oracle, "Oracle promotion requires its own scoped operation.")
    for operation in proposal.operations:
        if (
            operation.kind != "promote_oracle"
            or operation.artifact.id != oracle.id
            or operation.artifact_hash != digest(oracle)
            or operation.payload_hash != digest(oracle)
            or operation.target != oracle.id
            or operation.target_version != model.snapshot_id
        ):
            result.add("APPROVAL_SCOPE", oracle, "Promotion does not bind this exact oracle.")
    return result


def validate_oracle(
    oracle: Oracle, model: ProjectModel, context: TrustContext = NO_APPROVALS
) -> Result:
    result = Result()
    if not same_scope(oracle, model) or not same_scope(oracle.claim, model):
        result.add("SCOPE_NAMESPACE", oracle, "Oracle or claim reference is outside the namespace.")
    claim = next((item for item in model.claims if item.id == oracle.claim.id), None)
    if claim is None:
        result.add("ORACLE_CLAIM_MISSING", oracle, "Oracle claim does not exist.")
        return result
    # Validate the entire ancestor chain; a child cannot wash unusable evidence clean.
    pending = [claim]
    checked: set[str] = set()
    claims = {item.id: item for item in model.claims}
    while pending:
        current = pending.pop()
        if current.id in checked:
            continue
        checked.add(current.id)
        result.issues.extend(validate_claim(current, model).issues)
        pending.extend(claims[r.id] for r in current.derived_from if r.id in claims)
    if oracle.statement != claim.statement:
        result.add("ORACLE_STATEMENT", oracle, "Oracle statement differs from its supported claim.")
    if oracle.origin != claim.origin:
        result.add("ORACLE_ORIGIN_LEAKAGE", oracle, "Oracle silently changes its claim origin.")
    if oracle.inferred != claim.inferred or oracle.confidence > claim.confidence:
        result.add("ORACLE_UNCERTAINTY", oracle, "Oracle fails to preserve claim uncertainty.")
    if oracle.origin == "EXPLORATORY" and (oracle.normative or oracle.usage != "exploration"):
        result.add("ORACLE_EXPLORATORY", oracle, "Exploration cannot supply normative Pass/Fail.")
    if oracle.origin == "IMPLEMENTATION" and oracle.usage != "characterization":
        result.add(
            "ORACLE_IMPLEMENTATION", oracle, "Implementation supports characterization only."
        )
    if oracle.normative and oracle.usage == "exploration":
        result.add("ORACLE_EXPLORATORY", oracle, "Exploration cannot be normative.")
    if oracle.normative and (oracle.inferred or oracle.origin == "RISK"):
        invariant = claims.get(oracle.invariant_claim.id) if oracle.invariant_claim else None
        policy_backed = False
        if invariant is not None and oracle.invariant_claim is not None:
            invariant_result = validate_claim(invariant, model)
            policy_backed = (
                same_scope(oracle.invariant_claim, model)
                and invariant_result.valid
                and invariant.origin in {"CONTRACT", "ORGANIZATIONAL_POLICY"}
                and not invariant.inferred
                and not invariant.derived_from
                and invariant.statement == oracle.statement
            )
        if not policy_backed:
            result.issues.extend(oracle_approval(oracle, model, context).issues)
    return result
