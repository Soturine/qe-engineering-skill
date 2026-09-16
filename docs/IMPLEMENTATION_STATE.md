# Implementation State

- Active milestone: **M4 — Semantic QE & Production Agent Skill**
- Current stage: **M4.D1 — Technical Preview UX validated and frozen for presentation**
- Completed stages: M0, M1, M2, M3 and M4.H0–M4.H4
- Next checkpoint after presentation: M4.H5 — real-world semantic ingestion
- Last known green implementation checkpoint: `65528974a72a4994be3490424b303d70ea5de388`
  (workflow `35060484764`, Linux/Windows passed)
- H4 validation: local/package suite 319 passed, one local symlink skip; remote gates green
- Final H4/D1 local validation: 327 tests/evals passed against source and installed wheel, one local symlink
  skip; Ruff, format, mypy, dependency audit, schema reproduction and demo smoke passed; remote
  Linux/Windows validation of the provider-relation addendum passed
- Known incomplete work: live provider adapters, real-document semantic orchestration, downstream stale propagation, TMS integration and production-skill capabilities are not implemented
- Known deferred work: H5-H11 after presentation; M6 retrieval/change impact/deep audit after M4;
  M5 automation and external integrations after M6. No release/tag created.

`M4_PRODUCT_KISS_ADDENDUM.md` is the accepted product addendum for H3-H11. It narrows
implementation to the smallest useful, defensible path while preserving all trust invariants.

The skipped test requires Windows symlink privileges. The test remains enabled and CI must exercise it on a capable runner.
