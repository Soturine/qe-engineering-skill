# Standards and Methods Baseline

Status: **Methodological reference policy**

External standards and testing bodies provide taxonomies, techniques and control checklists. They do **not** automatically define a project's business behavior.

## References to consider by applicability

- ISTQB testing techniques and terminology;
- ISO/IEC 25010 quality characteristics;
- OWASP ASVS and OWASP Web/API guidance;
- NIST Secure Software Development Framework and relevant security guidance;
- WCAG/accessibility guidance where user interfaces are in scope;
- language/framework/platform security and reliability guidance;
- industry/regulatory standards only when applicable to the analyzed project.

## Usage rule

Standards can:

- suggest a risk family;
- define an organizational-policy control when explicitly adopted;
- provide test design techniques;
- strengthen security/accessibility/reliability review.

Standards cannot silently:

- invent business workflow;
- invent a UI path;
- invent an exact message;
- override approved project requirements;
- become a normative oracle unless applicable law/regulation, adopted policy or project authority makes them normative.

## Versioning

When a standard materially affects generated controls, record the standard/version or retrieval date in project/run metadata where practical. Avoid silently changing normative behavior because an external checklist changed.
