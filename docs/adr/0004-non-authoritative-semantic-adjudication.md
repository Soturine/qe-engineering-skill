# ADR 0004: non-authoritative semantic adjudication

Status: accepted for M4.H4.

H4 builds a small bounded pairwise graph over validated H3 normalization records. It classifies
`CONSISTENT`, `CONFLICTING`, `REFINEMENT`, `SUPERSEDED`, `DEPLOYMENT_INSTANCE`, `AMBIGUOUS` and
`HUMAN_DECISION_REQUIRED` relations. This is not GraphRAG and creates no retrieval infrastructure.

Every edge binds exact record hashes and preserves the authority/lifecycle context copied from
source evidence. Authority may explain context but never erases a divergence. Confidence is not
used to choose a winner. Conflicts remain explicit, ambiguous/provider-disagreement cases require
human review, and every adjudication has `winner = null`, `facts_promoted = false` and
`provider_self_authorized = false`.

Deterministic equality and grounded-detail comparison operate on candidate interpretations, not
terminal semantic truth. Unsupported subject alignment stays ambiguous. H4 invokes the H3
reconstruction validator with the full evidence envelope and current ledger before comparing.
Incomplete or stale inputs fail closed. Conflicts always require human review.

`SUPERSEDED` and `DEPLOYMENT_INSTANCE` are reserved vocabulary, not automatically emitted:
source lifecycle alone does not identify a replacement, and implementation agreement does not
prove a deployment relationship. Explicit relationship evidence is required for future support.

Optional `RELATE` provider output is accepted only through a fully reconstructed H2 candidate
envelope. Its pair IDs must resolve to current H3 records and its evidence must cite the sources of
both records. The proposed relation remains visibly separate from the deterministic relation. It
can turn an otherwise ambiguous pair into `HUMAN_DECISION_REQUIRED`, but cannot override a
mechanically proven relation, select a winner or alter authority. Provider/deterministic
disagreement is explicit and requires review.
