from qe_skill import domain as d
from qe_skill.m3 import materialize_oracle, reuse_oracle

from .helpers import minimal, ref


def test_contract_claim_materializes_exact_normative_oracle() -> None:
    model = minimal()
    result = materialize_oracle(d.Ref.model_validate(ref("claim")), model)
    assert result.status == "MATERIALIZED_NORMATIVE"
    assert result.oracle is not None and result.oracle.normative
    assert result.oracle.statement == model.claims[0].statement


def test_expected_text_cannot_strengthen_claim() -> None:
    model = minimal()
    result = materialize_oracle(
        d.Ref.model_validate(ref("claim")), model, expected_text="The record is always retained."
    )
    assert result.status == "UNSUPPORTED"
    assert result.oracle is None


def test_implementation_claim_is_characterization_only() -> None:
    model = minimal()
    model.claims[0].origin = "IMPLEMENTATION"
    model.ledger.sources[0].authority_class = "IMPLEMENTATION"
    result = materialize_oracle(d.Ref.model_validate(ref("claim")), model)
    assert result.status == "MATERIALIZED_CHARACTERIZATION"
    assert result.oracle is not None
    assert not result.oracle.normative
    assert result.oracle.usage == "characterization"


def test_risk_claim_is_exploratory_not_normative() -> None:
    model = minimal()
    model.claims[0].origin = "RISK"
    model.ledger.sources[0].authority_class = "GUIDANCE"
    result = materialize_oracle(d.Ref.model_validate(ref("claim")), model)
    assert result.status == "EXPLORATORY_ONLY"
    assert result.oracle is not None and not result.oracle.normative


def test_mutated_evidence_blocks_materialization_and_stale_reuse() -> None:
    model = minimal()
    model.ledger.sources[0].content_hash = "b" * 64
    result = materialize_oracle(d.Ref.model_validate(ref("claim")), model)
    assert result.status == "BLOCKED_SOURCE"
    assert reuse_oracle(d.Ref.model_validate(ref("oracle")), model).status == "UNSUPPORTED"


def test_foreign_clone_oracle_is_not_reused() -> None:
    model = minimal()
    foreign = d.Ref(id="oracle", project_id="source-project", snapshot_id="old")
    assert reuse_oracle(foreign, model).status == "BLOCKED_SOURCE"
