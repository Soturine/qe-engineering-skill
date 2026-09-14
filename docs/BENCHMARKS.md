# Public Benchmark Landscape — September 2026

This document records public references studied while defining the project. It is not a claim that any vendor is deficient internally; comparisons are limited to publicly documented capabilities.

## GitHub Awesome Copilot — Quality Playbook

Source: https://github.com/github/awesome-copilot/blob/main/skills/quality-playbook/SKILL.md

Publicly documented strengths:

- phased repository exploration and QA playbook;
- run metadata and coverage tracking;
- specification/repository discovery;
- adversarial iterations and terminal gate;
- designed to run in coding-agent environments including Claude/Copilot/Codex-style runtimes.

Lessons adopted:

- explore before generating;
- explicit run metadata;
- multi-phase quality gates;
- self-audit/eval mindset.

Design difference here:

- code behavior is not silently promoted to business contract;
- source completeness/provenance are separate enforceable contracts;
- manual test execution is the initial target;
- physical/human operations are an optional risk domain;
- normative oracles require primary-source resolution.

## paranoid-qa test-cases skill

Source: https://github.com/akovalion/paranoid-qa/blob/main/skills/test-cases/SKILL.md

Publicly documented strengths:

- collect all sources before generation;
- explicit `studied`/`not studied` reporting and honest blocked-source handling;
- account for requirements, mockups and implementation;
- detailed test-case authoring/TMS workflow.

Lessons adopted:

- no silent degradation;
- source completeness table;
- ambiguity should become a question, not an invented behavior.

Design difference here:

- source ledger and oracle provenance are machine schemas, not only writing rules;
- authority and confidence are separate dimensions;
- missing evidence can mechanically block readiness.

## BrowserStack AI Test Management agents

Sources:

- https://www.browserstack.com/docs/test-management/browserstack-ai
- https://www.browserstack.com/docs/test-management/browserstack-ai/ai-generated-test-cases

Publicly documented strengths:

- test-case generation from requirements, PDFs, screenshots and linked work systems;
- existing test repository context;
- dedicated agents for maintenance, test data, deduplication, test selection and failure analysis;
- manual-to-low-code automation path.

Lessons adopted:

- separate lifecycle concerns into modules;
- treat deduplication and maintenance as first-class;
- generate data/boundaries systematically;
- preserve future manual→automation path.

Design difference here:

- completeness gate across configured project sources;
- primary-evidence oracle provenance;
- explicit contract vs implementation vs risk separation;
- local/private-first architecture target;
- generic physical/human risk pack.

## Katalon AI-assisted test generation

Source: https://docs.katalon.com/katalon-platform/create-tests/generate-test-cases-with-ai

Publicly documented strengths:

- requirements to manual cases/steps;
- ALM integrations including Azure DevOps;
- AI-assisted test design/maintenance.

Lessons adopted:

- requirement→manual-case workflow;
- TMS integration is a renderer/adapter concern.

## Tricentis agentic testing

Public documentation: https://docs.tricentis.com/

Relevant lesson: preserve human-in-the-loop/co-creation for complex or consequential operations rather than assuming full autonomy is always desirable.

## Azure DevOps Test Plans

Sources:

- https://learn.microsoft.com/en-us/azure/devops/test/create-test-cases?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/test/share-steps-between-test-cases?view=azure-devops

Publicly documented capabilities relevant to the adapter:

- manual cases with individual action/expected-result steps;
- Shared Steps for reusable sequences;
- parameters/shared parameters for data-driven cases;
- separate cases for materially different workflows.

Design implication: generated tests should map to the real TMS model instead of inventing UI concepts the runner does not support.

## Microsoft GraphRAG

Source: https://microsoft.github.io/graphrag/

Relevant lesson: graph-based retrieval can help answer global questions over large corpora and relate entities/claims across documents.

Constraint adopted here: graph/LLM-derived claims are discovery artifacts, not primary evidence. They must resolve back to source spans/symbols before becoming an oracle.

## Landscape conclusion

Public tooling already does many individual pieces extremely well: repository audit, test generation, deduplication, test data, maintenance, ALM integration, agentic execution and advanced retrieval. The target differentiation of this repository is the **combination** of:

- complete-source honesty;
- machine-verifiable provenance;
- contract/implementation/risk separation;
- manual-first executability;
- risk coverage without test-count inflation;
- optional physical/human-process modeling;
- vendor-neutral Agent Skill interface;
- strict anti-invention gates;
- future automation from the same approved test model.

This should be validated empirically through evals rather than treated as a marketing claim.
