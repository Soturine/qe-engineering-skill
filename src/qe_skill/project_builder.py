"""Conservative M1 Project Model construction from typed deterministic extractions."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from typing import Literal, cast

from pydantic import Field, JsonValue, ValidationError

from qe_skill import domain as d
from qe_skill.parsers import ExtractionRecord, ParseResult


class BuildIssue(d.Record):
    code: str = Field(min_length=1)
    extraction_id: str = Field(min_length=1)
    source: d.Ref
    message: str = Field(min_length=1)
    severity: Literal["error", "warning"] = "error"


class ProjectBuild(d.Artifact):
    status: Literal["BUILT", "PARTIAL", "FAILED"]
    model: d.ProjectModel
    issues: list[BuildIssue]


COLLECTIONS = frozenset(
    {
        "requirements",
        "atomic_criteria",
        "entities",
        "fields",
        "constraints",
        "relationships",
        "actors",
        "roles",
        "groups",
        "actor_mappings",
        "permissions",
        "states",
        "transitions",
        "channels",
        "actions",
        "events",
        "interfaces",
        "integrations",
        "invariants",
        "ambiguities",
        "conflicts",
        "aliases",
        "existing_tests",
        "existing_results",
        "verified_paths",
    }
)


def _ref(identifier: str, project_id: str, snapshot_id: str) -> d.Ref:
    return d.Ref(id=identifier, project_id=project_id, snapshot_id=snapshot_id)


def _text(value: JsonValue | None, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text")
    return value


def _optional_text(value: JsonValue | None) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _strings(value: JsonValue | None, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ValueError(f"{field} must be a list of non-empty identifiers")
    return cast(list[str], value)


def _refs(value: JsonValue | None, field: str, project_id: str, snapshot_id: str) -> list[d.Ref]:
    return [_ref(item, project_id, snapshot_id) for item in _strings(value, field)]


def _name(record: Mapping[str, JsonValue]) -> str:
    for key in ("name", "title", "id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    raise ValueError("record needs an explicit id and name/title")


def _node_id(record: Mapping[str, JsonValue]) -> str:
    return _text(record.get("id"), "id")


def _claim_statement(record: Mapping[str, JsonValue]) -> str:
    for key in ("statement", "description", "title", "name", "id"):
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value
    raise ValueError("record has no evidence text for its claim")


def _origin(source: d.Source) -> d.Origin:
    return {
        "CONTRACT": "CONTRACT",
        "TECHNICAL_CONTRACT": "CONTRACT",
        "ORGANIZATIONAL_POLICY": "ORGANIZATIONAL_POLICY",
        "IMPLEMENTATION": "IMPLEMENTATION",
        "HISTORICAL": "IMPLEMENTATION",
        "GUIDANCE": "EXPLORATORY",
    }[source.authority_class]  # type: ignore[return-value]


def _claim_id(extraction: ExtractionRecord, suffix: str = "") -> str:
    payload = f"{extraction.id}\0{suffix}".encode()
    return f"claim.{hashlib.sha256(payload).hexdigest()[:24]}"


def _semantic_id(prefix: str, extraction: ExtractionRecord, suffix: str = "") -> str:
    payload = f"{extraction.id}\0{suffix}".encode()
    return f"{prefix}.{hashlib.sha256(payload).hexdigest()[:24]}"


def _claim(
    extraction: ExtractionRecord,
    source: d.Source,
    statement: str,
    *,
    suffix: str = "",
) -> d.Claim:
    return d.Claim(
        id=_claim_id(extraction, suffix),
        project_id=extraction.project_id,
        snapshot_id=extraction.snapshot_id,
        statement=statement,
        origin=_origin(source),
        evidence=[
            d.Evidence(
                source=extraction.source,
                source_hash=extraction.source_hash,
                location=extraction.location,
            )
        ],
        inferred=False,
        confidence=extraction.confidence,
        extraction=d.Extraction(method=extraction.extraction_method, version="1.0"),
        conflict="none",
    )


def _historical(value: JsonValue | None) -> d.HistoricalIdentity:
    if not isinstance(value, dict):
        raise ValueError("historical identity is required")
    return d.HistoricalIdentity.model_validate(value)


def _common(
    record: Mapping[str, JsonValue],
    claim: d.Claim,
    project_id: str,
    snapshot_id: str,
) -> dict[str, object]:
    return {
        "id": _node_id(record),
        "project_id": project_id,
        "snapshot_id": snapshot_id,
        "name": _name(record),
        "claims": [_ref(claim.id, project_id, snapshot_id).model_dump()],
    }


def _build_structured_node(
    collection: str,
    record: Mapping[str, JsonValue],
    claim: d.Claim,
    project_id: str,
    snapshot_id: str,
) -> d.Node:
    common = _common(record, claim, project_id, snapshot_id)

    def r(value: JsonValue | None, field: str) -> dict[str, object]:
        return _ref(_text(value, field), project_id, snapshot_id).model_dump()

    def rs(value: JsonValue | None, field: str) -> list[dict[str, object]]:
        return [item.model_dump() for item in _refs(value, field, project_id, snapshot_id)]

    if collection == "requirements":
        return d.Requirement.model_validate(
            {**common, "kind": "requirement", "lifecycle": record.get("lifecycle", "unknown")}
        )
    if collection == "atomic_criteria":
        return d.AtomicCriterion.model_validate(
            {
                **common,
                "kind": "atomic_criterion",
                "requirement": r(record.get("requirement_id"), "requirement_id"),
                "statement": _text(record.get("statement"), "statement"),
                "states": rs(record.get("state_ids"), "state_ids"),
                "actors": rs(record.get("actor_ids"), "actor_ids"),
                "channels": rs(record.get("channel_ids"), "channel_ids"),
                "boundaries": rs(record.get("boundary_ids"), "boundary_ids"),
                "timing": rs(record.get("timing_ids"), "timing_ids"),
                "failure_modes": rs(record.get("failure_mode_ids"), "failure_mode_ids"),
            }
        )
    if collection == "entities":
        return d.Entity.model_validate(
            {
                **common,
                "kind": "entity",
                "category": record.get("category", "unknown"),
                "fields": rs(record.get("field_ids"), "field_ids"),
                "relationships": rs(record.get("relationship_ids"), "relationship_ids"),
                "constraints": rs(record.get("constraint_ids"), "constraint_ids"),
                "states": rs(record.get("state_ids"), "state_ids"),
            }
        )
    if collection == "fields":
        required = record.get("required", "unknown")
        return d.ModelField.model_validate(
            {
                **common,
                "kind": "field",
                "entity": r(record.get("entity_id"), "entity_id"),
                "data_type": record.get("data_type", "unknown"),
                "required": required,
                "constraints": rs(record.get("constraint_ids"), "constraint_ids"),
                "aliases": _strings(record.get("aliases"), "aliases"),
            }
        )
    if collection == "constraints":
        return d.Constraint.model_validate(
            {
                **common,
                "kind": "constraint",
                "statement": _text(record.get("statement"), "statement"),
            }
        )
    if collection == "relationships":
        return d.Relationship.model_validate(
            {
                **common,
                "kind": "relationship",
                "from_entity": r(record.get("from_entity_id"), "from_entity_id"),
                "to_entity": r(record.get("to_entity_id"), "to_entity_id"),
                "relationship_type": record.get("relationship_type", "unknown"),
                "cardinality": _optional_text(record.get("cardinality")),
                "constraints": rs(record.get("constraint_ids"), "constraint_ids"),
            }
        )
    if collection in {"actors", "roles", "groups"}:
        if collection == "actors":
            return d.Actor.model_validate({**common, "kind": "actor"})
        if collection == "roles":
            return d.Role.model_validate({**common, "kind": "role"})
        return d.Group.model_validate({**common, "kind": "group"})
    if collection == "actor_mappings":
        return d.ActorMapping.model_validate(
            {
                **common,
                "kind": "actor_mapping",
                "actor": r(record.get("actor_id"), "actor_id"),
                "roles": rs(record.get("role_ids"), "role_ids"),
                "groups": rs(record.get("group_ids"), "group_ids"),
                "status": record.get("status", "unresolved"),
            }
        )
    if collection == "permissions":
        return d.Permission.model_validate(
            {
                **common,
                "kind": "permission",
                "subject": r(record.get("subject_id"), "subject_id"),
                "resource": r(record.get("resource_id"), "resource_id"),
                "action": r(record.get("action_id"), "action_id"),
                "scope": _text(record.get("scope"), "scope"),
                "effect": record.get("effect", "conditional"),
                "conditions": rs(record.get("condition_ids"), "condition_ids"),
            }
        )
    if collection == "states":
        return d.State.model_validate(
            {
                **common,
                "kind": "state",
                "entity": r(record.get("entity_id"), "entity_id"),
                "terminal": record.get("terminal", "unknown"),
            }
        )
    if collection == "transitions":
        from_id = _optional_text(record.get("from_state_id"))
        to_id = _optional_text(record.get("to_state_id"))
        return d.Transition.model_validate(
            {
                **common,
                "kind": "transition",
                "entity": r(record.get("entity_id"), "entity_id"),
                "from_state": r(from_id, "from_state_id") if from_id else None,
                "to_state": r(to_id, "to_state_id") if to_id else None,
                "trigger": r(record.get("trigger_id"), "trigger_id"),
                "actors": rs(record.get("actor_ids"), "actor_ids"),
                "roles": rs(record.get("role_ids"), "role_ids"),
                "channels": rs(record.get("channel_ids"), "channel_ids"),
                "preconditions": rs(record.get("precondition_ids"), "precondition_ids"),
                "guards": rs(record.get("guard_ids"), "guard_ids"),
                "postconditions": rs(record.get("postcondition_ids"), "postcondition_ids"),
                "side_effects": rs(record.get("side_effect_ids"), "side_effect_ids"),
                "exceptions": rs(record.get("exception_ids"), "exception_ids"),
                "classification": record.get("classification", "unknown"),
            }
        )
    if collection == "channels":
        return d.Channel.model_validate(
            {
                **common,
                "kind": "channel",
                "channel_type": record.get("channel_type", "other"),
                "interfaces": rs(record.get("interface_ids"), "interface_ids"),
            }
        )
    if collection == "actions":
        return d.Action.model_validate(
            {
                **common,
                "kind": "action",
                "actors": rs(record.get("actor_ids"), "actor_ids"),
                "input_constraints": rs(record.get("input_constraint_ids"), "input_constraint_ids"),
                "output_claims": rs(record.get("output_claim_ids"), "output_claim_ids"),
                "side_effects": rs(record.get("side_effect_ids"), "side_effect_ids"),
            }
        )
    if collection == "events":
        delivery = _optional_text(record.get("delivery_claim_id"))
        ordering = _optional_text(record.get("ordering_claim_id"))
        return d.Event.model_validate(
            {
                **common,
                "kind": "event",
                "producer": _text(record.get("producer"), "producer"),
                "consumer": _text(record.get("consumer"), "consumer"),
                "delivery_claim": r(delivery, "delivery_claim_id") if delivery else None,
                "ordering_claim": r(ordering, "ordering_claim_id") if ordering else None,
            }
        )
    if collection == "interfaces":
        optional_claims = {
            field: r(identifier, f"{field}_claim_id") if identifier else None
            for field in (
                "authentication",
                "authorization",
                "timeout",
                "retry",
                "idempotency",
                "ordering",
                "failure_behavior",
            )
            if (identifier := _optional_text(record.get(f"{field}_claim_id"))) is not None
        }
        contract_source_ids = record.get("contract_source_ids")
        contract_sources = (
            rs(contract_source_ids, "contract_source_ids")
            if contract_source_ids is not None
            else [claim.evidence[0].source.model_dump()]
        )
        return d.Interface.model_validate(
            {
                **common,
                "kind": "interface",
                "interface_type": record.get("interface_type", "other"),
                "producer": record.get("producer", "unknown"),
                "consumer": record.get("consumer", "unknown"),
                "contract_sources": contract_sources,
                "implementation_symbols": _strings(
                    record.get("implementation_symbols"), "implementation_symbols"
                ),
                **optional_claims,
            }
        )
    if collection == "integrations":
        return d.Integration.model_validate(
            {
                **common,
                "kind": "integration",
                "interfaces": rs(record.get("interface_ids"), "interface_ids"),
                "producer": _text(record.get("producer"), "producer"),
                "consumer": _text(record.get("consumer"), "consumer"),
            }
        )
    if collection == "invariants":
        return d.Invariant.model_validate(
            {
                **common,
                "kind": "invariant",
                "statement": _text(record.get("statement"), "statement"),
                "origin": claim.origin,
                "scope": _text(record.get("scope"), "scope"),
            }
        )
    if collection == "ambiguities":
        resolution = _optional_text(record.get("resolution_claim_id"))
        return d.Ambiguity.model_validate(
            {
                **common,
                "kind": "ambiguity",
                "question": _text(record.get("question"), "question"),
                "affected": rs(record.get("affected_ids"), "affected_ids"),
                "risk_of_guessing": _text(record.get("risk_of_guessing"), "risk_of_guessing"),
                "status": record.get("status", "open"),
                "resolution_claim": r(resolution, "resolution_claim_id") if resolution else None,
            }
        )
    if collection == "aliases":
        return d.Alias.model_validate(
            {
                **common,
                "kind": "alias",
                "canonical": r(record.get("canonical_id"), "canonical_id"),
                "alias": _text(record.get("alias"), "alias"),
                "confidence": record.get("confidence", 1.0),
                "status": record.get("status", "proposed"),
            }
        )
    if collection == "existing_tests":
        return d.ExistingTest.model_validate(
            {
                **common,
                "kind": "existing_test",
                "historical": _historical(record.get("historical")).model_dump(),
                "original_text": _text(record.get("original_text"), "original_text"),
                "classification": record.get("classification", "UNKNOWN"),
            }
        )
    if collection == "existing_results":
        test_id = _optional_text(record.get("test_id"))
        return d.ExistingResult.model_validate(
            {
                **common,
                "kind": "existing_result",
                "historical": _historical(record.get("historical")).model_dump(),
                "test": r(test_id, "test_id") if test_id else None,
                "outcome": record.get("outcome", "UNKNOWN"),
                "observed_at": _optional_text(record.get("observed_at")),
                "original_text": _text(record.get("original_text"), "original_text"),
            }
        )
    if collection == "verified_paths":
        steps = record.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("verified path needs explicit steps")
        path_steps: list[dict[str, object]] = []
        for step in steps:
            if not isinstance(step, dict):
                raise ValueError("verified path step must be an object")
            path_steps.append(
                {
                    "instruction": _text(step.get("instruction"), "instruction"),
                    "claim": r(step.get("claim_id"), "claim_id"),
                }
            )
        return d.VerifiedPath.model_validate(
            {
                **common,
                "kind": "verified_path",
                "path_type": record.get("path_type", "mixed"),
                "steps": path_steps,
                "verification_status": record.get("verification_status", "unresolved"),
            }
        )
    raise ValueError(f"unsupported semantic collection: {collection}")


def _build_conflict(
    record: Mapping[str, JsonValue],
    claim: d.Claim,
    node_claims: Mapping[str, list[d.Ref]],
    project_id: str,
    snapshot_id: str,
) -> d.Conflict:
    claim_refs: list[d.Ref] = []
    for identifier in _strings(record.get("conflicting_node_ids"), "conflicting_node_ids"):
        claim_refs.extend(node_claims.get(identifier, []))
    claim_refs.extend(
        _refs(record.get("conflicting_claim_ids"), "conflicting_claim_ids", project_id, snapshot_id)
    )
    resolution = _optional_text(record.get("resolution_claim_id"))
    return d.Conflict.model_validate(
        {
            **_common(record, claim, project_id, snapshot_id),
            "kind": "conflict",
            "conflicting_claims": [item.model_dump() for item in claim_refs],
            "affected": [
                item.model_dump()
                for item in _refs(
                    record.get("affected_ids"), "affected_ids", project_id, snapshot_id
                )
            ],
            "status": record.get("status", "unresolved"),
            "resolution_claim": _ref(resolution, project_id, snapshot_id).model_dump()
            if resolution
            else None,
        }
    )


def _issue(
    extraction: ExtractionRecord,
    code: str,
    message: str,
    severity: Literal["error", "warning"] = "error",
) -> BuildIssue:
    return BuildIssue(
        code=code,
        extraction_id=extraction.id,
        source=extraction.source,
        message=message,
        severity=severity,
    )


def build_project_model(ledger: d.SourceLedger, parses: Iterable[ParseResult]) -> ProjectBuild:
    """Build only facts explicitly represented by supported deterministic extractors."""

    sources = {source.id: source for source in ledger.sources}
    claims: list[d.Claim] = []
    nodes: list[d.Node] = []
    issues: list[BuildIssue] = []
    node_by_id: dict[str, d.Node] = {}
    node_payloads: dict[str, str] = {}
    node_claims: dict[str, list[d.Ref]] = {}
    deferred_conflicts: list[tuple[ExtractionRecord, Mapping[str, JsonValue], d.Claim]] = []
    openapi_actions: dict[str, d.Action] = {}
    openapi_interfaces: dict[str, d.Interface] = {}

    records = sorted(
        (record for parse in parses if parse.status == "PARSED" for record in parse.extractions),
        key=lambda record: (record.source.id, record.location, record.kind, record.id),
    )
    for extraction in records:
        source = sources.get(extraction.source.id)
        if (
            source is None
            or source.content_hash != extraction.source_hash
            or extraction.project_id != ledger.project_id
            or extraction.snapshot_id != ledger.snapshot_id
            or extraction.source.project_id != ledger.project_id
            or extraction.source.snapshot_id != ledger.snapshot_id
        ):
            issues.append(
                _issue(
                    extraction, "BUILD_SOURCE_UNUSABLE", "Extraction source is absent or mutated."
                )
            )
            continue
        if extraction.kind.startswith("openapi_"):
            if extraction.interpretation != "explicit" or extraction.inferred:
                issues.append(
                    _issue(
                        extraction,
                        "BUILD_INFERENCE_BLOCKED",
                        "Non-explicit OpenAPI extraction cannot enter the Project Model.",
                    )
                )
                continue
            claim = _claim(extraction, source, extraction.text)
            claims.append(claim)
            claim_ref = _ref(claim.id, ledger.project_id, ledger.snapshot_id)
            operation = extraction.attributes.get("operation")
            if extraction.kind == "openapi_operation":
                name = extraction.name or extraction.text
                action = d.Action(
                    id=_semantic_id("action.openapi", extraction),
                    project_id=ledger.project_id,
                    snapshot_id=ledger.snapshot_id,
                    name=name,
                    claims=[claim_ref],
                )
                interface = d.Interface(
                    id=_semantic_id("interface.openapi", extraction),
                    project_id=ledger.project_id,
                    snapshot_id=ledger.snapshot_id,
                    name=name,
                    claims=[claim_ref],
                    interface_type="http_api",
                    producer="unknown",
                    consumer="unknown",
                    contract_sources=[extraction.source],
                )
                channel = d.Channel(
                    id=_semantic_id("channel.openapi", extraction),
                    project_id=ledger.project_id,
                    snapshot_id=ledger.snapshot_id,
                    name=f"API channel for {name}",
                    claims=[claim_ref],
                    channel_type="api",
                    interfaces=[_ref(interface.id, ledger.project_id, ledger.snapshot_id)],
                )
                nodes.extend([action, interface, channel])
                openapi_actions[name] = action
                openapi_interfaces[name] = interface
            elif extraction.kind == "openapi_parameter" and isinstance(operation, str):
                parameter_action = openapi_actions.get(operation)
                if parameter_action is not None:
                    constraint = d.Constraint(
                        id=_semantic_id("constraint.openapi", extraction),
                        project_id=ledger.project_id,
                        snapshot_id=ledger.snapshot_id,
                        name=extraction.name or extraction.text,
                        claims=[claim_ref],
                        statement=extraction.text,
                    )
                    nodes.append(constraint)
                    parameter_action.input_constraints.append(
                        _ref(constraint.id, ledger.project_id, ledger.snapshot_id)
                    )
            elif extraction.kind == "openapi_response" and isinstance(operation, str):
                response_action = openapi_actions.get(operation)
                if response_action is not None:
                    response_action.output_claims.append(claim_ref)
            elif extraction.kind == "openapi_security" and isinstance(operation, str):
                secured_interface = openapi_interfaces.get(operation)
                if secured_interface is not None:
                    secured_interface.authorization = claim_ref
            elif extraction.kind == "openapi_schema":
                entity = d.Entity(
                    id=_semantic_id("entity.openapi", extraction),
                    project_id=ledger.project_id,
                    snapshot_id=ledger.snapshot_id,
                    name=extraction.name or extraction.text,
                    claims=[claim_ref],
                    category="technical",
                )
                required = extraction.attributes.get("required_fields")
                required_names = (
                    {item for item in required if isinstance(item, str)}
                    if isinstance(required, list)
                    else set()
                )
                properties = extraction.attributes.get("properties")
                property_types: dict[str, str] = {}
                if isinstance(properties, list):
                    for property_record in properties:
                        if not isinstance(property_record, dict):
                            continue
                        property_name = property_record.get("name")
                        property_type = property_record.get("type")
                        if isinstance(property_name, str):
                            property_types[property_name] = (
                                property_type if isinstance(property_type, str) else "unknown"
                            )
                field_names = sorted(required_names | property_types.keys())
                for index, field_name in enumerate(field_names):
                    field = d.ModelField(
                        id=_semantic_id("field.openapi", extraction, str(index)),
                        project_id=ledger.project_id,
                        snapshot_id=ledger.snapshot_id,
                        name=field_name,
                        claims=[claim_ref],
                        entity=_ref(entity.id, ledger.project_id, ledger.snapshot_id),
                        data_type=property_types.get(field_name, "unknown"),
                        required=field_name in required_names,
                    )
                    nodes.append(field)
                    entity.fields.append(_ref(field.id, ledger.project_id, ledger.snapshot_id))
                nodes.append(entity)
            continue
        if extraction.kind == "project_model_record":
            if extraction.interpretation != "explicit" or extraction.inferred:
                issues.append(
                    _issue(
                        extraction,
                        "BUILD_INFERENCE_BLOCKED",
                        "Inferred semantic records cannot enter the normative Project Model.",
                    )
                )
                continue
            collection = extraction.attributes.get("collection")
            value = extraction.attributes.get("value")
            if (
                not isinstance(collection, str)
                or collection not in COLLECTIONS
                or not isinstance(value, dict)
            ):
                issues.append(
                    _issue(
                        extraction,
                        "BUILD_UNSUPPORTED_RECORD",
                        "Structured semantic record is unsupported.",
                    )
                )
                continue
            try:
                claim = _claim(extraction, source, _claim_statement(value))
                if collection == "conflicts":
                    claims.append(claim)
                    deferred_conflicts.append((extraction, value, claim))
                    continue
                extra_claims: list[d.Claim] = []
                if collection == "verified_paths":
                    path_value = dict(value)
                    raw_steps = path_value.get("steps")
                    if not isinstance(raw_steps, list):
                        raise ValueError("verified path needs explicit steps")
                    normalized_steps: list[JsonValue] = []
                    for index, raw_step in enumerate(raw_steps):
                        if not isinstance(raw_step, dict):
                            raise ValueError("verified path step must be an object")
                        instruction = _text(raw_step.get("instruction"), "instruction")
                        step_claim = _claim(
                            extraction,
                            source,
                            instruction,
                            suffix=f"path-step-{index}",
                        )
                        extra_claims.append(step_claim)
                        normalized_steps.append({**raw_step, "claim_id": step_claim.id})
                    path_value["steps"] = normalized_steps
                    value = path_value
                node = _build_structured_node(
                    collection, value, claim, ledger.project_id, ledger.snapshot_id
                )
                claims.extend([claim, *extra_claims])
            except (ValueError, ValidationError):
                issues.append(
                    _issue(
                        extraction,
                        "BUILD_INVALID_RECORD",
                        "Semantic record failed its typed contract.",
                    )
                )
                continue
            payload = json.dumps(
                node.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            )
            existing = node_by_id.get(node.id)
            if existing is None:
                nodes.append(node)
                node_by_id[node.id] = node
                node_payloads[node.id] = payload
                node_claims[node.id] = list(node.claims)
            elif node_payloads[node.id] == payload:
                existing.claims.append(_ref(claim.id, ledger.project_id, ledger.snapshot_id))
                node_claims[node.id].append(_ref(claim.id, ledger.project_id, ledger.snapshot_id))
            else:
                conflict_digest = hashlib.sha256((node.id + extraction.id).encode()).hexdigest()
                automatic = d.Conflict(
                    id=f"conflict.{conflict_digest[:24]}",
                    project_id=ledger.project_id,
                    snapshot_id=ledger.snapshot_id,
                    name=f"Conflicting definitions for {node.id}",
                    claims=[],
                    conflicting_claims=[
                        *node_claims[node.id],
                        _ref(claim.id, ledger.project_id, ledger.snapshot_id),
                    ],
                    affected=[_ref(node.id, ledger.project_id, ledger.snapshot_id)],
                    status="unresolved",
                )
                nodes.append(automatic)
                issues.append(
                    _issue(
                        extraction,
                        "BUILD_CONFLICT",
                        "Conflicting explicit definitions were preserved.",
                        "warning",
                    )
                )

    for extraction, conflict_value, claim in deferred_conflicts:
        try:
            nodes.append(
                _build_conflict(
                    conflict_value,
                    claim,
                    node_claims,
                    ledger.project_id,
                    ledger.snapshot_id,
                )
            )
        except (ValueError, ValidationError):
            issues.append(
                _issue(
                    extraction, "BUILD_INVALID_CONFLICT", "Conflict record lacks resolvable claims."
                )
            )

    model = d.ProjectModel.model_validate(
        {
            "id": "project-model",
            "project_id": ledger.project_id,
            "snapshot_id": ledger.snapshot_id,
            "ledger": ledger.model_dump(mode="json"),
            "claims": [claim.model_dump(mode="json") for claim in claims],
            "oracles": [],
            "nodes": [node.model_dump(mode="json") for node in nodes],
            "tests": {
                "id": "test-model",
                "project_id": ledger.project_id,
                "snapshot_id": ledger.snapshot_id,
                "test_cases": [],
                "proposal_only": True,
            },
        }
    )
    return ProjectBuild(
        id="project-build",
        project_id=ledger.project_id,
        snapshot_id=ledger.snapshot_id,
        status="PARTIAL" if issues else "BUILT",
        model=model,
        issues=issues,
    )
