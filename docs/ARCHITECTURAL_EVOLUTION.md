# Architectural evolution

This is a retrospective, not a claim that every successor capability is implemented or qualified.

## Earlier approach: evidence-first QE

The original skill aimed to combine agent reasoning with a deterministic trust engine. Its technical preview included source inventory and extraction, structured models, audit and risk analysis, manual case proposals and validators. The runtime was substantial, including document parsing and case materialization; the full production agent experience remained incomplete. See the preserved [implementation status](STATUS.md).

## Current design direction

```text
User objective + selected original sources
  -> host agent: comprehension, interpretation, judgment
  <-> native tools: read, inspect, execute, measure
  -> agent: semantic artifacts and review
  -> deterministic shell: identity, scope, validation, integrity
  -> evidence, explicit unknowns, authorized actions
```

This is not a single mandatory pipeline. The agent may use native capabilities, existing tools, or a bounded fallback in whichever order resolves the uncertainty. For a PDF, read original pages and visual content when possible, and use extracted text for navigation and verification. Report missing visuals or unsupported formats; never assert complete reading from the text layer alone. For test execution, use the native runner rather than inventing a browser engine; generated real test code is legitimate, fabricated runner evidence is not.

The [FTD native-first branch](https://github.com/Soturine/functional-test-designer/tree/feat/native-first-reading) is a concrete example of this direction, not a statement that the branch is already merged or qualified.

## Responsibility split

- Agent: domain understanding, conflict resolution, risk reasoning, tool selection, authorship and interpretation of observations.
- Runtime: exact protocol parsing, scope enforcement, hashes, schemas, revision/identity, permission boundaries, reproducible accounting and verified transport.
- Native tools: real execution or measurement; their reports are evidence of what they observed, not automatically proof of approved business behavior.
- Human/authority: approves normative decisions, external writes and material unresolved trade-offs.

Keep these responsibilities distinct. Do not create a shared runtime or mandatory dependency solely because projects share principles.

## Reference material

[Agent Skills specification](https://agentskills.io/specification), [Building Effective Agents](https://www.anthropic.com/research/building-effective-agents), [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices), [Playwright Reporter API](https://playwright.dev/docs/api/class-reporter). These are design references, not evidence of successor qualification.

See [lessons learned](LESSONS_LEARNED.md) and [successor ledger](SUCCESSOR_PROJECTS.md).
