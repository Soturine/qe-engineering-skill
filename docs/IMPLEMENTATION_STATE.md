# Implementation State

- Active milestone: **M3 — Test Generation & Improvement**
- Current stage: **M3.1 — Authoring contracts and schemas**
- Completed stages: M0, M1 and M2; M3.0; M3.1 contracts/schema implementation
- Pending stage: M3.2 — oracle materialization and trust validation
- Last known green commit: `ed86200f99c479b14a60c1dd8151d15aec19b90e`
- Last validation: Windows, Python 3.12.10 — Ruff, format and strict mypy passed; focused M3/schema tests `36 passed`
- Known incomplete work: M3 oracle, authoring, improvement, candidate, rendering and CLI stages remain pending
- Known deferred work: external TMS writes (M4), execution/automation (M5), and change-impact/retrieval/release hardening (M6)

The skipped test requires Windows symlink privileges. The test remains enabled and CI must exercise it on a capable runner.
