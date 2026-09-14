# Source Authority Policy

Status: **Normative design policy**

## Purpose

Authority answers which source may define expected behavior. Confidence answers how certain an extraction or interpretation is. Freshness answers whether evidence is current. These dimensions must never be collapsed into one score.

## Default authority template

Each project may override precedence explicitly. A typical starting point is:

1. applicable law, regulation, contractual obligation, or formally approved external standard;
2. approved product/business specification, requirement, business rule, use case, acceptance criterion;
3. approved technical contract such as ADR, protocol, OpenAPI/AsyncAPI schema, data contract or interface specification;
4. explicit organizational engineering/security/quality policy;
5. current implementation evidence: source code, migrations, configuration and runtime behavior;
6. existing automated/manual tests, manuals, runbooks and operational evidence;
7. external guidance, community knowledge and heuristics.

This order is not universal. A project must record its authority configuration and source lifecycle. A stale high-authority source creates a divergence; it does not disappear silently.

## Conflict rules

- Never choose a source because it is easier to implement or has a newer filesystem timestamp.
- If configured precedence legitimately resolves expected behavior, preserve the lower-authority conflicting claim as a divergence.
- If precedence is insufficient, emit a conflict and block dependent normative output.
- Implementation may characterize current behavior but must not silently redefine approved product behavior.
- Existing tests are evidence of intended or historical behavior, not proof of correctness by themselves.
- Manuals/screenshots may confirm paths or labels without automatically outranking formal contracts.
- External standards can propose risk controls; they become normative only through applicable law/regulation, explicit project policy, approved requirement, or a policy-backed invariant.

## Source lifecycle

Sources may be `draft`, `approved`, `active`, `superseded`, `deprecated`, `archived`, or `unknown`. Supersession relationships should be explicit when known. Timestamps are supporting metadata, not authority.

## Authority versus oracle origin

`authority_class` belongs to the Source Ledger. `oracle.origin` explains why an Expected Result is permitted: `CONTRACT`, `IMPLEMENTATION`, `ORGANIZATIONAL_POLICY`, `RISK`, or `EXPLORATORY`.

A high-confidence implementation claim remains `IMPLEMENTATION`; confidence never promotes it to `CONTRACT`.

## Required implementation behavior

Every normative oracle must expose a reconstructable decision path:

`oracle → claim → source locator/span/symbol → authority decision`

If that chain cannot be reconstructed, the oracle is not publishable.
