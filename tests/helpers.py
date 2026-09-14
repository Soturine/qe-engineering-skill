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


def representative() -> ProjectModel:
    """Generic two-entity, permission, three-state model with an executable manual case."""
    model = minimal()
    data = model.model_dump(mode="json")

    def node(identifier: str, kind: str, **fields: object) -> dict[str, object]:
        return {
            **ref(identifier),
            "kind": kind,
            "name": identifier,
            "claims": [ref("claim")],
            **fields,
        }

    def supported(text: str) -> dict[str, object]:
        identifier = f"instruction-{len(data['claims'])}"
        claim = claim_copy(model, identifier)
        claim.statement = text
        data["claims"].append(claim.model_dump(mode="json"))
        return {"text": text, "claims": [ref(identifier)]}

    path_action = supported("Open the synthetic record endpoint with the prepared identifier.")
    data["nodes"] = [
        node(
            "entity-a",
            "entity",
            category="business",
            fields=[ref("field")],
            states=[ref("state-0"), ref("state-1"), ref("state-2")],
            relationships=[ref("relationship")],
        ),
        node("entity-b", "entity", category="technical"),
        node("constraint", "constraint", statement="The synthetic identifier is required."),
        node(
            "field",
            "field",
            entity=ref("entity-a"),
            data_type="string",
            required=True,
            constraints=[ref("constraint")],
        ),
        node(
            "relationship",
            "relationship",
            from_entity=ref("entity-a"),
            to_entity=ref("entity-b"),
            relationship_type="references",
        ),
        node("actor", "actor"),
        node("role", "role"),
        node("group", "group"),
        node(
            "mapping",
            "actor_mapping",
            actor=ref("actor"),
            roles=[ref("role")],
            groups=[ref("group")],
            status="confirmed",
        ),
        node(
            "permission",
            "permission",
            subject=ref("role"),
            resource=ref("entity-a"),
            action=ref("action"),
            scope="synthetic project",
            effect="allow",
        ),
        *[node(f"state-{i}", "state", entity=ref("entity-a"), terminal=i == 2) for i in range(3)],
        node("action", "action", actors=[ref("actor")]),
        node("event", "event", producer="synthetic producer", consumer="synthetic consumer"),
        node(
            "normal",
            "transition",
            entity=ref("entity-a"),
            from_state=ref("state-0"),
            to_state=ref("state-1"),
            trigger=ref("action"),
            classification="normal",
            actors=[ref("actor")],
            channels=[ref("api")],
            exceptions=[ref("exception")],
        ),
        node(
            "exception",
            "transition",
            entity=ref("entity-a"),
            from_state=ref("state-1"),
            to_state=ref("state-2"),
            trigger=ref("event"),
            classification="exception",
        ),
        node("api", "channel", channel_type="api", interfaces=[ref("interface")]),
        node("cli", "channel", channel_type="cli", interfaces=[]),
        node(
            "interface",
            "interface",
            interface_type="http_api",
            producer="synthetic producer",
            consumer="synthetic consumer",
            contract_sources=[ref("source")],
        ),
        node(
            "integration",
            "integration",
            producer="synthetic producer",
            consumer="synthetic consumer",
            interfaces=[ref("interface")],
        ),
        node("requirement", "requirement", lifecycle="approved"),
        node(
            "atom",
            "atomic_criterion",
            requirement=ref("requirement"),
            statement="The synthetic record is retained.",
            actors=[ref("actor")],
            states=[ref("state-1")],
            channels=[ref("api")],
        ),
        node(
            "invariant",
            "invariant",
            statement="The synthetic record is retained.",
            origin="CONTRACT",
            scope="synthetic record",
        ),
        node(
            "risk",
            "risk",
            category="data",
            description="Synthetic loss risk",
            affected=[ref("entity-a")],
            severity="medium",
            scale="low/medium/high/critical",
            derivation="Synthetic failure-mode analysis",
        ),
        node(
            "scenario",
            "scenario",
            origin="CONTRACT",
            preconditions=[ref("state-1")],
            stimulus=ref("action"),
            oracle=ref("oracle"),
            risks=[ref("risk")],
            selected_for_test=True,
            selection_reason="Covers the synthetic atomic criterion",
        ),
        node(
            "risk-scenario",
            "scenario",
            origin="RISK",
            preconditions=[],
            stimulus=ref("event"),
            oracle=None,
            risks=[ref("risk")],
            selected_for_test=False,
            selection_reason="Missing failure oracle; retain as exploratory question",
        ),
        node(
            "ambiguity",
            "ambiguity",
            question="What occurs on the synthetic failure?",
            affected=[ref("risk-scenario")],
            risk_of_guessing="Unsupported failure behavior",
            status="open",
        ),
        node(
            "path",
            "verified_path",
            path_type="api",
            verification_status="verified",
            steps=[{"instruction": path_action["text"], "claim": path_action["claims"][0]}],
        ),
    ]
    data["tests"]["test_cases"] = [
        {
            **ref("test"),
            "title": "Retain the synthetic record",
            "objective": "Verify retention",
            "origin": "CONTRACT",
            "claims": [ref("claim")],
            "criteria": [ref("atom")],
            "risks": [ref("risk")],
            "scenarios": [ref("scenario")],
            "environment": supported("Use the isolated synthetic environment."),
            "build": "synthetic-1",
            "actor": ref("actor"),
            "profile": "synthetic role",
            "permissions": [ref("permission")],
            "preconditions": [supported("Prepare one synthetic record in the intermediate state.")],
            "data": [
                {
                    "name": "identifier",
                    "properties": supported("Use the prepared record identifier."),
                    "preparation": supported("Record the identifier during preparation."),
                    "parameter": True,
                }
            ],
            "steps": [
                {
                    "number": 1,
                    "action": path_action,
                    "path": ref("path"),
                    "oracle": ref("oracle"),
                    "expected_result": "The synthetic record is retained.",
                    "required": True,
                    "evidence_expectation": "Record the observed identifier if validation fails.",
                }
            ],
            "pass_rule": "All required steps satisfy their oracles.",
            "fail_rule": "A required step contradicts its oracle; identify the failed step.",
            "blocked_rule": "Required preparation or observation cannot be completed.",
            "cleanup": supported("Discard the isolated synthetic environment after the test."),
            "isolation": supported("Use a fresh isolated synthetic environment for every run."),
            "shared_step_candidates": [],
            "parameter_candidates": ["identifier"],
            "readiness": "READY",
            "blocking_notes": [],
            "review_required": False,
        }
    ]
    data["nodes"].append(node("generated", "generated_test", test_case=ref("test")))
    return ProjectModel.model_validate(data)
