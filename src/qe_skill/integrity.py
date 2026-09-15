"""Project graph and manual-execution gates over the M0 contracts."""

from collections.abc import Iterator

from pydantic import BaseModel

from qe_skill import domain as d
from qe_skill.validation import (
    NO_APPROVALS,
    Result,
    TrustContext,
    same_scope,
    validate_approval,
    validate_claim,
    validate_ledger,
    validate_oracle,
)


def records(value: object) -> Iterator[BaseModel]:
    if isinstance(value, BaseModel):
        yield value
        for name in type(value).model_fields:
            yield from records(getattr(value, name))
    elif isinstance(value, list):
        for item in value:
            yield from records(item)


def refs(value: object) -> Iterator[d.Ref]:
    for record in records(value):
        if isinstance(record, d.Ref):
            yield record


def artifacts(model: d.ProjectModel) -> dict[str, d.Artifact]:
    return {r.id: r for r in records(model) if isinstance(r, d.Artifact)}


# Typed edge contracts. HistoricalIdentity deliberately has no Ref fields.
EDGE_TYPES: dict[tuple[type[BaseModel], str], tuple[type[d.Artifact], ...]] = {
    (d.Evidence, "source"): (d.Source,),
    (d.ScopeEntry, "source"): (d.Source,),
    (d.Claim, "derived_from"): (d.Claim,),
    (d.Oracle, "claim"): (d.Claim,),
    (d.Oracle, "invariant_claim"): (d.Claim,),
    (d.Entity, "fields"): (d.ModelField,),
    (d.Entity, "relationships"): (d.Relationship,),
    (d.Entity, "states"): (d.State,),
    (d.ModelField, "entity"): (d.Entity,),
    (d.Relationship, "from_entity"): (d.Entity,),
    (d.Relationship, "to_entity"): (d.Entity,),
    (d.ActorMapping, "actor"): (d.Actor,),
    (d.ActorMapping, "roles"): (d.Role,),
    (d.ActorMapping, "groups"): (d.Group,),
    (d.Permission, "subject"): (d.Actor, d.Role, d.Group),
    (d.Permission, "resource"): (d.Entity, d.Interface, d.Action),
    (d.Permission, "action"): (d.Action,),
    (d.Permission, "conditions"): (d.Constraint, d.Claim),
    (d.State, "entity"): (d.Entity,),
    (d.Transition, "entity"): (d.Entity,),
    (d.Transition, "from_state"): (d.State,),
    (d.Transition, "to_state"): (d.State,),
    (d.Transition, "trigger"): (d.Action, d.Event),
    (d.Transition, "preconditions"): (d.Claim, d.Constraint, d.State),
    (d.Transition, "guards"): (d.Claim, d.Constraint),
    (d.Transition, "postconditions"): (d.Claim, d.State),
    (d.Transition, "side_effects"): (d.Claim, d.Action, d.Event),
    (d.Transition, "exceptions"): (d.Transition, d.Claim),
    (d.Channel, "interfaces"): (d.Interface,),
    (d.Integration, "interfaces"): (d.Interface,),
    (d.Interface, "contract_sources"): (d.Source,),
    (d.AtomicCriterion, "requirement"): (d.Requirement,),
    (d.AtomicCriterion, "states"): (d.State,),
    (d.AtomicCriterion, "boundaries"): (d.Constraint,),
    (d.AtomicCriterion, "timing"): (d.Claim, d.Constraint),
    (d.AtomicCriterion, "failure_modes"): (d.Risk, d.Claim),
    (d.Conflict, "conflicting_claims"): (d.Claim,),
    (d.Alias, "canonical"): (d.Node,),
    (d.Scenario, "preconditions"): (d.Claim, d.State, d.Constraint),
    (d.Scenario, "stimulus"): (d.Action, d.Event),
    (d.Scenario, "oracle"): (d.Oracle,),
    (d.GeneratedTest, "test_case"): (d.TestCase,),
    (d.GeneratedTest, "replaces"): (d.ExistingTest,),
    (d.ExistingResult, "test"): (d.ExistingTest,),
    (d.PathStep, "claim"): (d.Claim,),
    (d.TestCase, "actor"): (d.Actor,),
    (d.TestCase, "permissions"): (d.Permission,),
    (d.TestCase, "criteria"): (d.AtomicCriterion,),
    (d.TestCase, "scenarios"): (d.Scenario,),
    (d.TestCase, "shared_step_candidates"): (d.VerifiedPath,),
    (d.ManualStep, "path"): (d.VerifiedPath,),
    (d.ManualStep, "oracle"): (d.Oracle,),
}
COMMON_EDGE_TYPES: dict[str, tuple[type[d.Artifact], ...]] = {
    "claims": (d.Claim,),
    "constraints": (d.Constraint,),
    "actors": (d.Actor,),
    "roles": (d.Role,),
    "channels": (d.Channel,),
    "risks": (d.Risk,),
    "resolution_claim": (d.Claim,),
    "authentication": (d.Claim,),
    "authorization": (d.Claim,),
    "timeout": (d.Claim,),
    "retry": (d.Claim,),
    "idempotency": (d.Claim,),
    "ordering": (d.Claim,),
    "failure_behavior": (d.Claim,),
    "delivery_claim": (d.Claim,),
    "ordering_claim": (d.Claim,),
    "input_constraints": (d.Constraint,),
    "output_claims": (d.Claim,),
}


def graph_integrity(model: d.ProjectModel) -> Result:
    result = Result()
    index: dict[str, d.Artifact] = {}
    for record in records(model):
        if isinstance(record, d.Artifact):
            if record.id in index:
                result.add("MODEL_DUPLICATE_ID", record, "Artifact identifier is duplicated.")
            index[record.id] = record
            if not same_scope(record, model):
                result.add("SCOPE_NAMESPACE", record, "Artifact is outside the project/snapshot.")
    for record in records(model):
        for name in type(record).model_fields:
            value = getattr(record, name)
            direct = (
                [value] if isinstance(value, d.Ref) else value if isinstance(value, list) else []
            )
            for reference in direct:
                if not isinstance(reference, d.Ref):
                    continue
                if not same_scope(reference, model):
                    result.add(
                        "SCOPE_NAMESPACE", reference.id, "Reference is outside the namespace."
                    )
                target = index.get(reference.id)
                if target is None:
                    result.add("MODEL_MISSING_REF", reference.id, "Referenced artifact is absent.")
                expected = EDGE_TYPES.get((type(record), name), COMMON_EDGE_TYPES.get(name))
                if expected and target is not None and not isinstance(target, expected):
                    result.add(
                        "MODEL_REF_TYPE", reference.id, "Reference targets the wrong node type."
                    )
    return result


def validate_nodes(model: d.ProjectModel) -> Result:
    result = Result()
    index = artifacts(model)
    for node in model.nodes:
        if not node.claims and not isinstance(node, d.Risk | d.Ambiguity | d.Conflict | d.Scenario):
            result.add("PROV_NODE_MISSING", node, "Semantic node has no evidence-bearing claims.")
        if isinstance(node, d.Transition):
            for state_ref in (node.from_state, node.to_state):
                state = index.get(state_ref.id) if state_ref else None
                if isinstance(state, d.State) and state.entity != node.entity:
                    result.add(
                        "MODEL_STATE_ENTITY", node, "Transition state belongs to another entity."
                    )
            if node.from_state is None and node.to_state is None:
                result.add(
                    "MODEL_TRANSITION_EMPTY", node, "Transition has no source or target state."
                )
        if isinstance(node, d.Entity):
            for ref in node.fields + node.states:
                child = index.get(ref.id)
                if isinstance(child, d.ModelField | d.State) and child.entity.id != node.id:
                    result.add(
                        "MODEL_ENTITY_OWNERSHIP", node, "Entity references another entity's child."
                    )
        if isinstance(node, d.VerifiedPath) and node.verification_status == "verified":
            for step in node.steps:
                claim = index.get(step.claim.id)
                if (
                    not isinstance(claim, d.Claim)
                    or claim.inferred
                    or step.instruction != claim.statement
                    or not validate_claim(claim, model).valid
                ):
                    result.add(
                        "PROV_PATH_UNVERIFIED", node, "Verified path lacks exact current evidence."
                    )
        if isinstance(node, d.Ambiguity | d.Conflict) and node.status == "resolved":
            resolution = index.get(node.resolution_claim.id) if node.resolution_claim else None
            if (
                not isinstance(resolution, d.Claim)
                or resolution.inferred
                or resolution.origin not in {"CONTRACT", "ORGANIZATIONAL_POLICY"}
                or not validate_claim(resolution, model).valid
            ):
                result.add(
                    "MODEL_RESOLUTION", node, "Resolution lacks an authoritative decision claim."
                )
        if isinstance(node, d.Invariant):
            for ref in node.claims:
                claim = index.get(ref.id)
                if isinstance(claim, d.Claim) and claim.origin != node.origin:
                    result.add("PROV_AUTHORITY", node, "Invariant changes supporting claim origin.")
    return result


def dependency_ids(test: d.TestCase, index: dict[str, d.Artifact]) -> set[str]:
    visited = {test.id}
    pending = list(refs(test))
    while pending:
        ref = pending.pop()
        if ref.id in visited:
            continue
        visited.add(ref.id)
        if ref.id in index:
            pending.extend(refs(index[ref.id]))
    return visited


def validate_test_case(
    test: d.TestCase,
    model: d.ProjectModel,
    context: TrustContext = NO_APPROVALS,
) -> Result:
    result = Result()
    result.issues.extend(graph_integrity(model).issues)
    result.issues.extend(validate_ledger(model.ledger).issues)
    result.issues.extend(validate_nodes(model).issues)
    index = artifacts(model)
    ready = test.readiness == "READY"
    if not same_scope(test, model):
        result.add("SCOPE_NAMESPACE", test, "Test Case is outside the model namespace.")
    for ref in refs(test):
        if not same_scope(ref, model) or ref.id not in index:
            result.add(
                "MODEL_MISSING_REF", test, "Test dependency is missing or outside the namespace."
            )
    if [step.number for step in test.steps] != list(range(1, len(test.steps) + 1)):
        result.add("READY_STEP_ORDER", test, "Manual step numbers must be unique and consecutive.")
    if test.origin == "EXPLORATORY":
        if (
            test.readiness != "EXPLORATORY_ONLY"
            or test.pass_rule is not None
            or test.fail_rule is not None
        ):
            result.add(
                "READY_EXPLORATORY", test, "Exploratory cases cannot declare normative Pass/Fail."
            )
    if ready:
        if (
            not test.steps
            or test.actor is None
            or not test.claims
            or test.pass_rule is None
            or test.fail_rule is None
        ):
            result.add(
                "READY_MANUAL_CONTEXT", test, "Ready case lacks execution or result context."
            )
        if test.review_required or test.blocking_notes:
            result.add(
                "READY_REVIEW_REQUIRED", test, "Outstanding review or blocking notes prevent READY."
            )
        if model.ledger.manifest.completeness not in {"COMPLETE", "SCOPED_COMPLETE"}:
            result.add("READY_SOURCE", test, "Partial or invalid evidence scope prevents READY.")
        for record in records(test):
            if isinstance(record, d.SupportedText):
                claims = [index.get(ref.id) for ref in record.claims]
                if not any(
                    isinstance(c, d.Claim)
                    and c.statement == record.text
                    and not c.inferred
                    and validate_claim(c, model).valid
                    for c in claims
                ):
                    result.add(
                        "READY_UNSUPPORTED_TEXT",
                        test,
                        "Operational instruction lacks an exact non-inferred supporting claim.",
                    )
        if not any(step.required and step.oracle is not None for step in test.steps):
            result.add("READY_NO_VALIDATION", test, "Ready case has no required validation step.")
        for permission_ref in test.permissions:
            permission = index.get(permission_ref.id)
            if isinstance(permission, d.Permission) and test.actor is not None:
                mapped = permission.subject.id == test.actor.id or any(
                    isinstance(node, d.ActorMapping)
                    and node.actor == test.actor
                    and node.status == "confirmed"
                    and permission.subject in node.roles + node.groups
                    for node in model.nodes
                )
                if not mapped:
                    result.add(
                        "READY_ACTOR_MAPPING",
                        test,
                        "Permission subject has no confirmed mapping to the test actor.",
                    )
    dependencies = dependency_ids(test, index)
    if ready:
        for identifier in dependencies:
            dependency = index.get(identifier)
            if isinstance(dependency, d.Node) and not isinstance(
                dependency, d.Risk | d.Scenario | d.Ambiguity | d.Conflict
            ):
                for claim_ref in dependency.claims:
                    claim = index.get(claim_ref.id)
                    if isinstance(claim, d.Claim) and (
                        claim.inferred or not validate_claim(claim, model).valid
                    ):
                        result.add(
                            "READY_INFERRED_MODEL",
                            test,
                            "Execution depends on unsupported or inferred model facts.",
                        )
    for node in model.nodes:
        if isinstance(node, d.Conflict | d.Ambiguity):
            unresolved = node.status in {"open", "unresolved"}
            affected = {ref.id for ref in node.affected}
            if isinstance(node, d.Conflict):
                affected.update(ref.id for ref in node.conflicting_claims)
            if ready and unresolved and dependencies.intersection(affected | {node.id}):
                result.add(
                    "READY_CONFLICT", test, "Unresolved conflict/ambiguity affects this case."
                )
        if isinstance(node, d.ActorMapping) and ready and node.id in dependencies:
            if node.status != "confirmed":
                result.add("READY_ACTOR_MAPPING", test, "Actor mapping is not confirmed.")
        if isinstance(node, d.Risk) and ready and node.id in dependencies:
            if node.category in {
                "security",
                "safety",
                "human_physical",
            } and node.severity.lower() in {
                "high",
                "critical",
            }:
                result.add(
                    "READY_REVIEW_REQUIRED", test, "High-consequence risk requires human review."
                )
    for step in test.steps:
        path = index.get(step.path.id)
        if ready and (
            not isinstance(path, d.VerifiedPath) or path.verification_status != "verified"
        ):
            result.add("READY_PATH", test, "Ready manual step requires a verified execution path.")
        oracle = index.get(step.oracle.id) if step.oracle else None
        if isinstance(oracle, d.Oracle):
            result.issues.extend(validate_oracle(oracle, model, context).issues)
            if step.expected_result != oracle.statement:
                result.add(
                    "ORACLE_EXPECTED_RESULT", test, "Step Expected Result differs from its oracle."
                )
            if test.origin != oracle.origin:
                result.add("ORACLE_ORIGIN_LEAKAGE", test, "Test origin differs from its oracle.")
            if ready and not oracle.normative:
                result.add("READY_ORACLE", test, "Ready validation requires a normative oracle.")
        elif step.expected_result is not None or (ready and step.required):
            result.add("ORACLE_MISSING", test, "Expected Result has no resolvable oracle.")
    return result


def validate_project_model(model: d.ProjectModel, context: TrustContext = NO_APPROVALS) -> Result:
    result = graph_integrity(model)
    result.issues.extend(validate_ledger(model.ledger).issues)
    for claim in model.claims:
        result.issues.extend(validate_claim(claim, model).issues)
    for oracle in model.oracles:
        result.issues.extend(validate_oracle(oracle, model, context).issues)
    result.issues.extend(validate_nodes(model).issues)
    for approval in model.approvals:
        proposal = next((p for p in model.proposals if p.id == approval.proposal_id), None)
        if proposal is None:
            result.add("APPROVAL_PROPOSAL_MISSING", approval, "Approval proposal is missing.")
        else:
            result.issues.extend(
                validate_approval(
                    approval, proposal, context, model.snapshot_id, proposal.target_snapshot
                ).issues
            )
    for test in model.tests.test_cases:
        result.issues.extend(validate_test_case(test, model, context).issues)
    return result
