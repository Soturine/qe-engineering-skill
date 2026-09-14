# Public Benchmark Landscape — September 2026

This document records public references studied while defining the project. It does not claim knowledge of private/internal capabilities. Lessons are design inputs, not copied requirements.

## Agent Skills open pattern

Sources:
- https://agentskills.io/
- https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills

Relevant ideas:
- `SKILL.md` plus optional references/scripts/assets;
- progressive disclosure;
- reusable procedural knowledge;
- portability across compatible agent environments.

Adopted:
- portable skill interface;
- thin orchestration layer;
- scripts/references loaded as needed.

Extended here:
- critical trust rules live in schemas/validators/evals, not prompt text alone.

## GitHub Awesome Copilot — Quality Playbook

Source:
- https://github.com/github/awesome-copilot/blob/main/skills/quality-playbook/SKILL.md

Strengths:
- phased repository exploration;
- coverage/run metadata;
- specification/repository discovery;
- adversarial iterations/terminal gate.

Adopted:
- explore before generation;
- explicit run metadata;
- multi-phase quality gates;
- self-audit/eval mindset.

Difference targeted here:
- code behavior is not silently promoted to business contract;
- source completeness/provenance are enforceable contracts;
- manual execution is the initial output;
- normative oracles resolve to primary evidence.

## paranoid-qa — test-cases

Source:
- https://github.com/akovalion/paranoid-qa/blob/main/skills/test-cases/SKILL.md

Strengths:
- collect all sources before generation;
- studied/not-studied honesty;
- requirements/mockups/implementation context;
- detailed TMS-oriented authoring.

Adopted:
- no silent source degradation;
- ambiguity becomes a question;
- source completeness is visible.

Extended:
- machine schemas for ledger/provenance;
- authority/confidence separated;
- missing evidence can mechanically block readiness.

## stellarlinkco/myclaude — test-cases

Source:
- https://github.com/stellarlinkco/myclaude/blob/master/skills/test-cases/SKILL.md

Relevant ideas:
- requirements/PRD → structured test cases;
- happy, negative and edge paths;
- traceability from source requirements to tests.

Adopted:
- structured generation only after requirements are understood;
- traceability is first-class.

Extended:
- generation is preceded by evidence audit, implementation comparison, risk analysis and oracle validation.

## Claude-Skills — test-scenarios

Source:
- https://github.com/borghei/Claude-Skills/blob/main/project-management/execution/test-scenarios/SKILL.md

Relevant ideas:
- scenario-level coverage before detailed cases;
- happy/edge/error/security/accessibility/performance lenses;
- coverage-gap thinking.

Adopted:
- map scenario universe before selecting cases.

Extended:
- scenario optimization and source-backed oracles prevent test-count inflation.

## skilldrop — test-plan-generator

Source:
- https://github.com/sananthanarayan/skilldrop/blob/main/skills/test-plan-generator/SKILL.md

Relevant ideas:
- requirements/PR/diff inputs;
- risk-based test-plan generation;
- acceptance-criteria mapping;
- explicit uncovered areas.

Adopted:
- change-impact and risk-based planning are future capabilities.

Extended:
- diff/code evidence cannot overwrite higher-authority product truth.

## Browserbase — ui-test

Source:
- https://github.com/browserbase/skills/blob/main/skills/ui-test/SKILL.md

Relevant idea:
- action → assertion/observable result discipline during UI execution.

Adopted:
- clear manual Action/Expected Result pairing.

Difference:
- routine Pass evidence remains proportional to risk; heavy evidence collection is not mandatory for every successful step.

## BrowserStack AI Test Management agents

Sources:
- https://www.browserstack.com/docs/test-management/browserstack-ai
- https://www.browserstack.com/docs/test-management/browserstack-ai/ai-generated-test-cases

Strengths:
- generation from documents/screenshots/linked work systems;
- existing test repository context;
- dedicated maintenance/data/dedup/selection/failure-analysis agents;
- manual-to-automation path.

Adopted:
- lifecycle concerns as modules;
- dedup/maintenance/data as first-class;
- future manual→automation path.

Target difference:
- verifiable configured-source completeness;
- primary-evidence oracle provenance;
- contract/implementation/policy/risk separation;
- local/private-first architecture;
- optional physical/human process pack.

## Katalon AI-assisted test generation

Source:
- https://docs.katalon.com/katalon-platform/create-tests/generate-test-cases-with-ai

Relevant ideas:
- requirements → manual cases/steps;
- ALM integration;
- project/test-object context;
- future API/automation assistance.

Adopted:
- TMS is a renderer/adapter, not the domain model.

## Tricentis agentic testing

Public documentation:
- https://docs.tricentis.com/

Relevant idea:
- human-in-the-loop/co-creation remains valuable for complex/consequential workflows.

Adopted:
- explicit human review gates rather than assuming autonomy is always desirable.

## TestMu AI / LambdaTest Agent Skills

Source:
- https://github.com/LambdaTest/agent-skills

Relevant ideas:
- modular skills across many testing frameworks/languages;
- portability;
- eval/playbook mindset.

Adopted:
- future automation via specialized adapters/skills rather than polluting the manual core.

## Greptile — graph-based codebase context

Source:
- https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context

Relevant idea:
- files/functions/classes/imports/dependencies form a useful code graph for impact analysis.

Adopted:
- AST/symbol/dependency graphs are preferred for structural code facts.

## Augment — semantic codebase context

Public material emphasizes multi-repository semantic context, history and engineering knowledge.

Relevant idea:
- semantic retrieval helps locate context across large codebases.

Constraint here:
- semantic retrieval supports discovery; source identity/primary evidence still governs truth.

## Microsoft GraphRAG

Source:
- https://microsoft.github.io/graphrag/

Relevant idea:
- graph-based retrieval can improve global questions and cross-document relation discovery.

Constraint:
- graph/LLM-derived claims are not primary evidence and must resolve to source spans/symbols before becoming an oracle.

## Azure DevOps Test Plans

Sources:
- https://learn.microsoft.com/en-us/azure/devops/test/create-test-cases?view=azure-devops
- https://learn.microsoft.com/en-us/azure/devops/test/share-steps-between-test-cases?view=azure-devops

Relevant native concepts:
- Action + Expected Result steps;
- Shared Steps;
- parameters/shared parameters;
- separate cases for materially different workflows.

Design implication:
- adapters map to real TMS concepts and must not invent runner UI.

## Landscape conclusion

Public tooling already covers many pieces well: repository audit, generation, maintenance, data, deduplication, ALM integration, execution and retrieval. The target differentiation of this repository is the combination of:

- complete-source honesty;
- machine-verifiable provenance;
- authority/confidence separation;
- contract/implementation/policy/risk separation;
- manual-first executability;
- atomic and risk coverage without count inflation;
- optional human/physical-process modeling;
- vendor-neutral Agent Skill interface;
- strict anti-invention gates;
- future automation from the same approved Test Model.

This is a hypothesis to validate with evals, not a superiority claim.
