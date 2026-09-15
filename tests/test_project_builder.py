import json
from pathlib import Path

from qe_skill import domain as d
from qe_skill.ingestion import ingest_local
from qe_skill.integrity import validate_project_model
from qe_skill.project_builder import build_project_model


def historical(identifier: str) -> dict[str, object]:
    return {
        "external_id": identifier,
        "source_project": "synthetic-history",
        "source_snapshot": "old",
        "version": "1",
        "history_locators": [f"synthetic://{identifier}"],
        "content_hash": "e" * 64,
    }


def representative_document() -> dict[str, object]:
    return {
        "qe_model": {
            "requirements": [
                {
                    "id": "requirement.retain",
                    "title": "Retain a record",
                    "statement": "The record is retained.",
                    "lifecycle": "approved",
                }
            ],
            "constraints": [
                {
                    "id": "constraint.identifier",
                    "name": "Identifier required",
                    "statement": "The identifier is required.",
                }
            ],
            "entities": [
                {
                    "id": "entity.record",
                    "name": "Record",
                    "category": "business",
                    "field_ids": ["field.identifier"],
                    "state_ids": ["state.new", "state.saved"],
                }
            ],
            "fields": [
                {
                    "id": "field.identifier",
                    "name": "identifier",
                    "entity_id": "entity.record",
                    "data_type": "string",
                    "required": True,
                    "constraint_ids": ["constraint.identifier"],
                }
            ],
            "actors": [{"id": "actor.operator", "name": "Operator"}],
            "roles": [{"id": "role.writer", "name": "Writer"}],
            "actor_mappings": [
                {
                    "id": "mapping.operator",
                    "name": "Operator writer mapping",
                    "actor_id": "actor.operator",
                    "role_ids": ["role.writer"],
                    "status": "confirmed",
                }
            ],
            "actions": [{"id": "action.save", "name": "Save record"}],
            "permissions": [
                {
                    "id": "permission.save",
                    "name": "Save permission",
                    "subject_id": "role.writer",
                    "resource_id": "entity.record",
                    "action_id": "action.save",
                    "scope": "synthetic project",
                    "effect": "allow",
                }
            ],
            "states": [
                {
                    "id": "state.new",
                    "name": "New",
                    "entity_id": "entity.record",
                    "terminal": False,
                },
                {
                    "id": "state.saved",
                    "name": "Saved",
                    "entity_id": "entity.record",
                    "terminal": True,
                },
            ],
            "interfaces": [
                {
                    "id": "interface.records",
                    "name": "Records API",
                    "interface_type": "http_api",
                    "producer": "synthetic service",
                    "consumer": "synthetic client",
                }
            ],
            "channels": [
                {
                    "id": "channel.api",
                    "name": "API",
                    "channel_type": "api",
                    "interface_ids": ["interface.records"],
                }
            ],
            "transitions": [
                {
                    "id": "transition.save",
                    "name": "Save transition",
                    "entity_id": "entity.record",
                    "from_state_id": "state.new",
                    "to_state_id": "state.saved",
                    "trigger_id": "action.save",
                    "actor_ids": ["actor.operator"],
                    "role_ids": ["role.writer"],
                    "channel_ids": ["channel.api"],
                    "classification": "normal",
                }
            ],
            "atomic_criteria": [
                {
                    "id": "criterion.retain",
                    "name": "Retention criterion",
                    "requirement_id": "requirement.retain",
                    "statement": "The record is retained.",
                    "state_ids": ["state.saved"],
                    "actor_ids": ["actor.operator"],
                    "channel_ids": ["channel.api"],
                }
            ],
            "invariants": [
                {
                    "id": "invariant.identifier",
                    "name": "Identifier retention",
                    "statement": "The saved record retains its identifier.",
                    "scope": "saved records",
                }
            ],
            "ambiguities": [
                {
                    "id": "ambiguity.retry",
                    "name": "Retry behavior",
                    "question": "What happens after a transport failure?",
                    "affected_ids": ["interface.records"],
                    "risk_of_guessing": "A guessed retry policy could duplicate writes.",
                    "status": "open",
                }
            ],
            "aliases": [
                {
                    "id": "alias.item",
                    "name": "Item alias",
                    "canonical_id": "entity.record",
                    "alias": "Item",
                    "confidence": 1.0,
                    "status": "confirmed",
                }
            ],
            "verified_paths": [
                {
                    "id": "path.save",
                    "name": "Save API path",
                    "path_type": "api",
                    "verification_status": "verified",
                    "steps": [{"instruction": "Send the record to the declared API interface."}],
                }
            ],
            "existing_tests": [
                {
                    "id": "existing.test",
                    "name": "Historical retention test",
                    "historical": historical("test-1"),
                    "original_text": "Check record retention.",
                    "classification": "UNKNOWN",
                }
            ],
            "existing_results": [
                {
                    "id": "existing.result",
                    "name": "Historical result",
                    "historical": historical("result-1"),
                    "test_id": "existing.test",
                    "outcome": "PASS",
                    "observed_at": "2026-01-01T00:00:00Z",
                    "original_text": "The historical run passed.",
                }
            ],
        }
    }


def ingest_document(tmp_path: Path, document: dict[str, object], snapshot: str = "v1"):
    (tmp_path / "model.json").write_text(json.dumps(document, ensure_ascii=False), encoding="utf-8")
    return ingest_local(
        tmp_path,
        project_id="synthetic",
        snapshot_id=snapshot,
        collected_at="2026-01-01T00:00:00Z",
    )


def test_representative_structured_project_builds_nontrivial_valid_model(tmp_path: Path) -> None:
    report = ingest_document(tmp_path, representative_document())
    model = report.build.model
    assert report.status == "COMPLETE"
    assert report.ledger.manifest.completeness == "SCOPED_COMPLETE"
    assert validate_project_model(model).valid
    assert len(model.nodes) >= 18
    assert {
        d.Requirement,
        d.Entity,
        d.ModelField,
        d.Actor,
        d.Role,
        d.Permission,
        d.State,
        d.Transition,
        d.Channel,
        d.Interface,
        d.AtomicCriterion,
        d.Invariant,
        d.Ambiguity,
        d.Alias,
        d.VerifiedPath,
        d.ExistingTest,
        d.ExistingResult,
    } <= {type(node) for node in model.nodes}
    source_ids = {source.id for source in model.ledger.sources}
    assert model.claims
    assert all(
        evidence.source.id in source_ids and evidence.source_hash
        for claim in model.claims
        for evidence in claim.evidence
    )
    assert all(not claim.inferred for claim in model.claims)
    assert model.oracles == [] and model.tests.test_cases == []


def test_unstructured_code_does_not_become_domain_contract(tmp_path: Path) -> None:
    (tmp_path / "service.py").write_text(
        "@route('/guessed')\ndef admin_delete():\n    return 'never executed'\n", encoding="utf-8"
    )
    report = ingest_local(
        tmp_path,
        project_id="synthetic",
        snapshot_id="v1",
        collected_at="2026-01-01T00:00:00Z",
        authority_class="IMPLEMENTATION",
    )
    assert report.status == "COMPLETE"
    assert report.parses[0].extractions
    assert report.build.model.claims == []
    assert report.build.model.nodes == []


def test_invalid_semantic_record_is_visible_and_prevents_complete(tmp_path: Path) -> None:
    report = ingest_document(
        tmp_path, {"qe_model": {"requirements": [{"title": "Missing explicit identity"}]}}
    )
    assert report.status == "PARTIAL"
    assert report.build.issues[0].code == "BUILD_INVALID_RECORD"
    assert report.ledger.sources[0].study_status == "PARTIALLY_STUDIED"
    assert report.ledger.manifest.completeness == "PARTIAL"


def test_conflicting_explicit_definitions_remain_visible(tmp_path: Path) -> None:
    first = {"qe_model": {"requirements": [{"id": "requirement.same", "title": "First"}]}}
    second = {"qe_model": {"requirements": [{"id": "requirement.same", "title": "Second"}]}}
    (tmp_path / "a.json").write_text(json.dumps(first), encoding="utf-8")
    (tmp_path / "b.json").write_text(json.dumps(second), encoding="utf-8")
    report = ingest_local(
        tmp_path,
        project_id="synthetic",
        snapshot_id="v1",
        collected_at="2026-01-01T00:00:00Z",
    )
    conflicts = [node for node in report.build.model.nodes if isinstance(node, d.Conflict)]
    assert report.status == "PARTIAL"
    assert len(conflicts) == 1 and conflicts[0].status == "unresolved"
    assert len(conflicts[0].conflicting_claims) == 2
    assert validate_project_model(report.build.model).valid


def test_repeated_runs_are_deterministic_and_project_isolated(tmp_path: Path) -> None:
    document = representative_document()
    first = ingest_document(tmp_path, document)
    second = ingest_document(tmp_path, document)
    assert first.model_dump() == second.model_dump()
    other = ingest_local(
        tmp_path,
        project_id="other",
        snapshot_id="v1",
        collected_at="2026-01-01T00:00:00Z",
    )
    assert {claim.id for claim in first.build.model.claims}.isdisjoint(
        {claim.id for claim in other.build.model.claims}
    )
    assert all(claim.project_id == "other" for claim in other.build.model.claims)


def test_raw_openapi_builds_structural_interface_nodes(tmp_path: Path) -> None:
    (tmp_path / "openapi.yaml").write_text(
        """openapi: 3.1.0
paths:
  /records/{record_id}:
    get:
      parameters:
        - name: record_id
          in: path
          required: true
      security:
        - bearer: []
      responses:
        '200': {description: Found}
components:
  schemas:
    Record:
      required: [record_id]
      properties:
        record_id: {type: string}
        label: {type: string}
""",
        encoding="utf-8",
    )
    report = ingest_local(
        tmp_path,
        project_id="synthetic",
        snapshot_id="v1",
        collected_at="2026-01-01T00:00:00Z",
        authority_class="TECHNICAL_CONTRACT",
        lifecycle="approved",
    )
    assert report.status == "COMPLETE"
    assert validate_project_model(report.build.model).valid
    assert {d.Interface, d.Action, d.Channel, d.Constraint, d.Entity, d.ModelField} <= {
        type(node) for node in report.build.model.nodes
    }
    interface = next(node for node in report.build.model.nodes if isinstance(node, d.Interface))
    assert interface.authorization is not None
    fields = [node for node in report.build.model.nodes if isinstance(node, d.ModelField)]
    assert {(field.name, field.data_type, field.required) for field in fields} == {
        ("label", "string", False),
        ("record_id", "string", True),
    }


def test_foreign_and_heuristic_extractions_cannot_enter_builder(tmp_path: Path) -> None:
    report = ingest_document(tmp_path, representative_document())
    foreign = report.parses[0].model_copy(deep=True)
    semantic = next(item for item in foreign.extractions if item.kind == "project_model_record")
    semantic.project_id = "foreign"
    semantic.source.project_id = "foreign"
    result = build_project_model(report.ledger, [foreign])
    assert "BUILD_SOURCE_UNUSABLE" in {issue.code for issue in result.issues}
    assert all(claim.project_id == "synthetic" for claim in result.model.claims)

    heuristic = report.parses[0].model_copy(deep=True)
    for extraction in heuristic.extractions:
        if extraction.kind == "project_model_record":
            extraction.interpretation = "heuristic"
            extraction.inferred = True
    result = build_project_model(report.ledger, [heuristic])
    assert "BUILD_INFERENCE_BLOCKED" in {issue.code for issue in result.issues}
    assert result.model.oracles == []
