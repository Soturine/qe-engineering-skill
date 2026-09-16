# Implementation State

- Active milestone: **M4 — Semantic QE & Production Agent Skill**
- Current stage: **M4.D1 — Technical Preview UX implemented locally; validation pending**
- Completed stages: M0, M1, M2, M3 and M4.H0–M4.H4
- Next checkpoint after green H4: M4.D1 — Technical Preview UX; do not start H5 before presentation
- Last known green: `8ed0bdb7c6233e6db6c5e0e0d2695f06932f6ef3` (workflow `35058770837`, Linux/Windows passed)
- H4 validation: local/package suite 319 passed, one local symlink skip; remote gates green
- Known incomplete work: live provider adapters, real-document semantic orchestration, downstream stale propagation, TMS integration and production-skill capabilities are not implemented
- Known deferred work: H5-H11 after presentation; M6 retrieval/change impact/deep audit after M4;
  M5 automation and external integrations after M6. No release/tag created.

`M4_PRODUCT_KISS_ADDENDUM.md` is the accepted product addendum for H3-H11. It narrows
implementation to the smallest useful, defensible path while preserving all trust invariants.

The skipped test requires Windows symlink privileges. The test remains enabled and CI must exercise it on a capable runner.
