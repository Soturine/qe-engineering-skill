# Implementation State

- Active milestone: **M4 — Integrations & Production Agent Skill**
- Current stage: **M4.H3 complete; M4.H4 is the next implementation checkpoint**
- Completed stages: M0, M1, M2, M3 and M4.H0–M4.H3
- Pending stage: M4.H4 — Semantic relations and adjudication
- Last known green commit before H3: `594048aa6ec4a7124a7255b4407cbc2ecf3ef4a9` (workflow `35039940164`, Linux/Windows passed)
- H3 validation: grounded multilingual normalization unit/adversarial/eval coverage plus the full quality workflow; see `M4_EVIDENCE.md`
- Known incomplete work: live provider adapters, real-document semantic orchestration, relation/adjudication, TMS integration and production-skill capabilities are not implemented
- Known deferred work: Semantic Reasoning Provider and external TMS integration are cataloged for M4; execution/automation is M5; whole-system audit, benchmarks, change impact, retrieval and release hardening are M6

`M4_PRODUCT_KISS_ADDENDUM.md` is the accepted product addendum for H3-H11. It narrows
implementation to the smallest useful, defensible path while preserving all trust invariants.

The skipped test requires Windows symlink privileges. The test remains enabled and CI must exercise it on a capable runner.
