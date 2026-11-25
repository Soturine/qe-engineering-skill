# Lessons learned — QE Engineering

Transition record, 2026-11-25. This repository was the first Agent Skill in this engineering portfolio. It explored source authority, risk, oracle validation, provenance and manual test authoring. It already intended an agent-first product, but the implemented runtime also owned substantial ingestion, model construction and case materialization. The lesson is not that deterministic software is bad: it is that semantic work should not be needlessly replaced by deterministic approximations.

## What to preserve

- Source authority is independent of confidence; distinguish approved obligations, implementation observations, risk hypotheses and exploratory questions.
- Source inventory is not reading; citations and hashes prove particular mechanical properties, not understanding or semantic entailment.
- Risk motivates investigation, not invented expected behavior. Atomic behavioral coverage matters more than case count.
- Preserve historical tests, runs, attachments and decisions. Revalidate imported assets against the target project; proposals do not grant write authority.
- Explicit scope, stable identity, hashes, schemas, revision binding, approval, reproducible measurement and safety checks are good uses of deterministic tooling.

## What to rethink

| Historical implementation | Lesson |
| --- | --- |
| [PDF extraction](../src/qe_skill/parsers.py) uses textual extraction with explicit limitations | Prefer original host-native reading (including visual evidence when supported); a text layer cannot establish completeness. Extractors remain useful for exact verification and disclosed fallback. |
| [Project builder](../src/qe_skill/project_builder.py) constructs structured evidence models | Let the agent discover relevant domain semantics; use mechanical contracts only where needed. |
| [Case authoring](../src/qe_skill/m3.py) materializes structured manual proposals | Prefer contextual semantic authorship over rigid templates or automatic scenario expansion; preserve the oracle. |
| [Reasoning boundary](../src/qe_skill/reasoning.py) defines provider contracts | Use the host's actual capabilities when adequate; a new provider interface is not automatically required. |
| [Trust model](TRUST_MODEL.md) and [oracle policy](ORACLE_POLICY.md) constrain claims | Retain the principles; verify objective invariants without confusing schema validity with truth. |

These examples are based on inspected code and policies, not a full audit of every module. A parser, AST, heuristic or algorithm can still be valuable when it provides an objective measurement, navigation aid, candidate or bounded fallback. Do not eliminate needed mechanisms merely to reduce code volume.

## Preferred direction

Agent-led: the agent investigates and decides meaning. Native-first: use original inputs through actual host capabilities. Tool-native: compose existing official skills, CLI, MCP, LSP and runners where useful and authorized. Runtime-verified: protect mechanics and evidence. Prefer progressive disclosure, adaptive orchestration and minimal justified dependencies. No fixed model or agent count is inherently required.

Qualification should compare real runs with independent gold, negative controls, equivalent wording, conflicting sources, visual-only facts and unavailable capabilities. Report false claims, actual scope, time and cost where available. A documentation change or green unit suite does not establish agent effectiveness.

See [architectural evolution](ARCHITECTURAL_EVOLUTION.md) and [transfer ledger](SUCCESSOR_PROJECTS.md).
