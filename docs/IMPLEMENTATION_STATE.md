# Implementation State

- Active milestone: **M4 — Integrations & Production Agent Skill**
- Current stage: **M4.H4 implementation; validation pending**
- Completed stages: M0, M1, M2, M3 and M4.H0–M4.H3
- Next checkpoint after green H4: M4.D1 — Technical Preview UX; do not start H5 before presentation
- Last known green: `a77b8efd406625596b2f751425ca37a3437c7685` (workflow `35042393752`, Linux/Windows passed)
- H4 validation: pending full local/package and remote gates; see `M4_EVIDENCE.md`
- Known incomplete work: live provider adapters, real-document semantic orchestration, downstream stale propagation, TMS integration and production-skill capabilities are not implemented
- Known deferred work: Semantic Reasoning Provider and external TMS integration are cataloged for M4; execution/automation is M5; whole-system audit, benchmarks, change impact, retrieval and release hardening are M6

`M4_PRODUCT_KISS_ADDENDUM.md` is the accepted product addendum for H3-H11. It narrows
implementation to the smallest useful, defensible path while preserving all trust invariants.

The skipped test requires Windows symlink privileges. The test remains enabled and CI must exercise it on a capable runner.
