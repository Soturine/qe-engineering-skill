# Public Quality-Engineering Landscape — September 2026

This document records public market direction relevant to the architecture. It is contextual research, not a normative requirement and not a claim about undisclosed internal capabilities of any organization.

## Direction of travel

Public material from quality-engineering vendors and consultancies increasingly emphasizes:

- GenAI-assisted requirements/test design;
- agentic test creation and maintenance;
- continuous quality engineering rather than isolated QA;
- self-healing and maintenance;
- test selection and failure analysis;
- governance, observability and auditability for AI/agentic systems;
- human review for consequential workflows.

## What is already becoming commodity

Capabilities that should not be treated as unique differentiators by themselves:

- generating many test cases from a PRD;
- converting natural language to Gherkin;
- drafting browser/mobile automation code;
- generating API tests from OpenAPI;
- summarizing test failures;
- asking an LLM to brainstorm edge cases.

## Target differentiation to validate empirically

This repository targets a stricter combination:

- verifiable source inventory before completeness claims;
- source→claim→oracle provenance;
- explicit contract vs implementation vs policy vs risk separation;
- manual-first operational executability;
- atomic coverage rather than only requirement-ID linkage;
- source conflict/ambiguity as first-class output;
- risk expansion without rewarding test-count inflation;
- optional human/physical-process analysis;
- vendor-neutral Agent Skill interface;
- local/private-first design;
- deterministic gates around model-assisted reasoning;
- the same approved Test Model feeding future automation.

These are engineering targets, not marketing claims. Evals must demonstrate the advantage.

## Community signal

Public QA communities repeatedly caution that AI can automate weak requirements and bloated test suites just as easily as strong ones. Community discussion is anecdotal and must not be treated as authority, but it supports measuring coverage quality, provenance and defect-detection value rather than raw case count.
