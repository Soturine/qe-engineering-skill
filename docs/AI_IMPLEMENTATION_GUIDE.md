# AI Implementation Guide

This guide exists so an implementation agent can continue the repository without relying on conversational history.

## Starting a task

1. Read `AGENTS.md`.
2. Identify the active roadmap milestone.
3. Read all normative docs relevant to that milestone.
4. Inspect the current tree, tests, schemas and ADRs.
5. State the smallest coherent change that advances an exit criterion.
6. Implement code + tests + docs together.
7. Run validations/evals.
8. Report exact status and remaining gaps.

## Do not jump ahead

Do not build a sophisticated generator, RAG stack, GraphRAG, Azure writer or browser automation before M0/M1 invariants can be tested. A fluent generator on weak trust foundations is a regression, not progress.

## How to use language models

Use models for:

- semantic extraction from unstructured text;
- relation/alias proposals;
- contradiction candidate detection;
- scenario ideation;
- test-step wording after the oracle exists;
- risk brainstorming.

Prefer deterministic code for:

- inventory;
- hashing/version identity;
- schema validation;
- exact code symbols/imports where parsers exist;
- duplicate IDs;
- status/gate transitions;
- output field limits;
- source-to-claim linkage validation.

## Provider adapters

Never scatter provider calls through domain code. Use an interface such as:

```python
class ReasoningProvider(Protocol):
    def extract(...): ...
    def relate(...): ...
    def synthesize(...): ...
```

Provider adapters may support Claude/OpenAI/others. Tests for core logic must not require a live model.

## Evaluation discipline

For model-assisted features, create fixtures before optimizing prompts. Keep expected properties more important than exact wording. Include false-positive penalties and unsupported-oracle checks.

## Documentation discipline

A future agent should be able to understand every architectural decision from the repository. If implementation relies on an unwritten conversational assumption, the change is not complete.
