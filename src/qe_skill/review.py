"""Offline review presentation; no reasoning, translation of evidence, or external writes."""

# Embedded HTML/CSS/JavaScript literals stay readable as complete presentation fragments.
# ruff: noqa: E501

from __future__ import annotations

import hashlib
import html
from collections.abc import Mapping

from pydantic import Field

from qe_skill import domain as d
from qe_skill.adjudication import RelationInput, SemanticRelationGraph, validate_relation_graph
from qe_skill.m2 import M2AnalysisReport
from qe_skill.m3 import M3GenerationReport, validate_generation_report


class ReviewContext(d.Record):
    project_model: d.ProjectModel
    analysis: M2AnalysisReport
    semantic_inputs: list[RelationInput] = Field(default_factory=list)
    relations: SemanticRelationGraph | None = None

    def validate_for(self, report: M3GenerationReport) -> None:
        if not validate_generation_report(report, self.project_model, self.analysis).valid:
            raise ValueError("Review context does not validate against the generation report.")
        if self.relations is not None:
            if (
                self.relations.project_id != report.project_id
                or self.relations.snapshot_id != report.snapshot_id
                or not validate_relation_graph(self.relations, self.semantic_inputs).valid
                or self.relations.status != "COMPLETE"
            ):
                raise ValueError("Semantic review context is stale, invalid or cross-scope.")


# Presentation keys/enums only. Source wording, IDs, paths and technical values are never translated.
PT = {
    "Test Plan": "Plano de Testes",
    "Overview": "Visão Geral",
    "Test Cases": "Casos de Teste",
    "Requirements": "Requisitos",
    "Criteria": "Critérios",
    "Risks": "Riscos",
    "Scenarios": "Cenários",
    "Conflicts": "Conflitos",
    "Gaps": "Lacunas",
    "Traceability": "Rastreabilidade",
    "Evidence": "Evidências",
    "Reviews": "Revisões",
    "Shared Steps": "Passos Compartilhados",
    "Technical details": "Detalhes técnicos",
    "Search": "Buscar por ID, título ou texto",
    "All": "Todos",
    "Status": "Estado",
    "Review": "Revisão",
    "Visible cases": "Casos visíveis",
    "Not supplied": "Não informado",
    "Reference unavailable": "Referência não disponível",
    "Proposal only; history unchanged.": "Somente proposta; histórico preservado.",
    "Context not supplied; source traceability is incomplete.": "Contexto não fornecido; rastreabilidade das fontes incompleta.",
    "Candidate relations; no normative winner or approval.": "Relações candidatas; sem vencedor normativo ou aprovação.",
    "Normative promotion blocked; affected tests not linked by H4.": "Promoção normativa bloqueada; testes afetados ainda não vinculados pela H4.",
    "Original": "Original",
    "Proposed": "Proposta",
    "Historical asset modified? NO": "Artefato histórico alterado? NÃO",
    "Used by:": "Utilizado por:",
    "id": "ID",
    "title": "Título",
    "name": "Nome",
    "statement": "Afirmação",
    "objective": "Objetivo",
    "action": "Ação",
    "origin": "Origem",
    "priority_rationale": "Justificativa de prioridade",
    "actor": "Ator",
    "profile": "Perfil",
    "permissions": "Permissões",
    "environment": "Ambiente",
    "build": "Build",
    "preconditions": "Pré-condições",
    "data": "Dados de Teste",
    "parameters": "Parâmetros",
    "steps": "Passos do Teste",
    "phase": "Fase",
    "expected_result": "Resultado Esperado",
    "evidence_expectation": "Evidência esperada",
    "evidence_expectations": "Evidências esperadas",
    "pass_rule": "Regra de aprovação",
    "fail_rule": "Regra de falha",
    "blocked_rule": "Regra de bloqueio",
    "cleanup": "Limpeza",
    "isolation": "Isolamento",
    "blocking_notes": "Notas de bloqueio",
    "blocking_reasons": "Motivos do bloqueio",
    "review_status": "Estado de revisão",
    "rationale": "Justificativa",
    "readiness": "Prontidão",
    "requirements": "Requisitos",
    "criteria": "Critérios",
    "risks": "Riscos",
    "scenarios": "Cenários",
    "primary_provenance": "Proveniência primária",
    "claims": "Afirmações",
    "claim": "Afirmação",
    "oracle": "Oráculo",
    "evidence": "Evidências",
    "source": "Fonte",
    "target": "Destino",
    "relation": "Relação",
    "text": "Texto original",
    "authority_class": "Autoridade",
    "lifecycle": "Ciclo de vida",
    "source_lifecycle": "Ciclo de vida da fonte",
    "source_language": "Idioma da fonte",
    "location": "Localização",
    "locator": "Localizador",
    "properties": "Propriedades",
    "preparation": "Preparação",
    "constraints": "Restrições",
    "candidate_values": "Valores candidatos",
    "partition": "Partição",
    "partitions": "Partições",
    "required": "Obrigatório",
    "number": "Número",
    "path": "Caminho",
    "unresolved_reasons": "Pendências",
    "shared_step_candidates": "Passos compartilhados candidatos",
    "parameter_candidates": "Parâmetros candidatos",
    "used_by": "Utilizado por:",
    "original_text": "Original",
    "proposed_case": "Proposta",
    "before": "Antes",
    "after": "Depois",
    "field": "Campo",
    "field_diffs": "Diferenças por campo",
    "step_diffs": "Diferenças por passo",
    "original_test": "Teste original",
    "human_review_required": "Revisão humana necessária",
    "outcome": "Resultado da adjudicação",
    "conflict_preserved": "Conflito preservado",
    "winner": "Vencedor",
    "rationale_codes": "Códigos de justificativa",
    "authority_context": "Contexto de autoridade",
    "left": "Afirmação A",
    "right": "Afirmação B",
    "left_authority": "Autoridade A",
    "right_authority": "Autoridade B",
    "left_lifecycle": "Ciclo de vida A",
    "right_lifecycle": "Ciclo de vida B",
    "original_statements": "Evidências originais",
    "meaning": "Interpretação candidata",
    "candidate_statement": "Afirmação candidata",
    "READY": "Pronto",
    "BLOCKED": "Bloqueado",
    "BLOCKED_SOURCE": "Fonte bloqueada",
    "READY_WITH_REVIEW": "Pronto com revisão",
    "REVIEW_REQUIRED": "Revisão necessária",
    "APPROVED": "Aprovado",
    "REJECTED": "Rejeitado",
    "PARTIAL": "Parcial",
    "COMPLETE": "Completo",
    "INVALID": "Inválido",
    "CONFLICTING": "Conflitante",
    "AMBIGUOUS": "Ambíguo",
    "UNSUPPORTED": "Não suportado",
    "FAILED": "Falhou",
    "PENDING_REVIEW": "Revisão pendente",
    "EXPLORATORY_ONLY": "Somente exploratório",
    "CONSISTENT": "Consistente",
    "REFINEMENT": "Refinamento",
    "HUMAN_DECISION_REQUIRED": "Decisão humana necessária",
    "PREPARATION": "Preparação",
    "NAVIGATION": "Navegação",
    "ACTION": "Ação",
    "VALIDATION": "Validação",
    "CLEANUP": "Limpeza",
    "CONTRACT": "Contrato",
    "IMPLEMENTATION": "Implementação",
    "GUIDANCE": "Orientação",
    "TECHNICAL_CONTRACT": "Contrato técnico",
    "HISTORICAL": "Histórico",
    "ORGANIZATIONAL_POLICY": "Política organizacional",
    "NEW": "Novo",
    "KEEP": "Manter",
    "IMPROVE": "Melhorar",
    "REVISE": "Revisar",
    "REPLACE": "Substituir",
    "GREENFIELD": "Projeto novo",
    "BROWNFIELD": "Projeto existente",
    "No validated exact supporting claim is available.": "Nenhuma afirmação de suporte exata e validada está disponível.",
    "Environment evidence is not available.": "Evidência de ambiente não está disponível.",
    "Cleanup evidence is not available.": "Evidência de limpeza não está disponível.",
    "Isolation evidence is not available.": "Evidência de isolamento não está disponível.",
    "Actor profile context is not available.": "Contexto de perfil do ator não está disponível.",
    "Actor/profile evidence is not available.": "Evidência de ator/perfil não está disponível.",
    "Build or version context is not available.": "Contexto de build ou versão não está disponível.",
    "No defensible normative oracle is available.": "Nenhum oráculo normativo defensável está disponível.",
    "Required evidence, preparation, action, or observation cannot be completed.": "A evidência, preparação, ação ou observação obrigatória não pode ser concluída.",
    "Generated from an explicitly selected M2 scenario without adding behavior.": "Gerado a partir de um cenário M2 explicitamente selecionado, sem adicionar comportamento.",
    "An explicitly modeled risk activates only its named category; no outcome is invented.": "Um risco modelado explicitamente ativa somente sua categoria; nenhum resultado é inventado.",
    "Record the observed result for any Fail or Blocked outcome.": "Registre o resultado observado para qualquer resultado Falhou ou Bloqueado.",
    "For a normal Pass, record the observation at the validating step.": "Para uma aprovação normal, registre a observação no passo de validação.",
    "For Fail or Blocked, record the affected step and diagnostic observation.": "Para Falhou ou Bloqueado, registre o passo afetado e a observação diagnóstica.",
    "No selected M2 scenarios were available.": "Nenhum cenário M2 selecionado estava disponível.",
}
ENUM_FIELDS = {
    "readiness",
    "action",
    "mode",
    "review_status",
    "status",
    "phase",
    "authority_class",
    "origin",
    "relation",
}
LOCALIZED_TEXT_FIELDS = {
    "title",
    "priority_rationale",
    "unresolved_reasons",
    "evidence_expectation",
    "evidence_expectations",
    "blocked_rule",
    "blocking_notes",
    "blocking_reasons",
    "rationale",
    "limitations",
}
TECHNICAL = {
    "schema_version",
    "project_id",
    "snapshot_id",
    "configuration",
    "input_binding",
    "manifest",
    "materialized_test",
    "extraction",
    "provider_identity",
}


def localize_presentation_text(value: str, field: str, language: str) -> str:
    """Localize only engine-owned presentation strings, never source evidence or identifiers."""
    if language != "pt-BR":
        return value
    if field in ENUM_FIELDS:
        return PT.get(value, value)
    if field not in LOCALIZED_TEXT_FIELDS:
        return value
    if value.startswith("Review scenario "):
        return "Revisar cenário " + value.removeprefix("Review scenario ")
    if value.startswith("Prepare: "):
        return "Preparar: " + value.removeprefix("Prepare: ")
    if value.startswith("Reusable setup for "):
        return "Preparação reutilizável para " + value.removeprefix("Reusable setup for ")
    return PT.get(value, value)


CSS = """
:root{color-scheme:light;--ink:#172b43;--muted:#475569;--line:#cbd5e1;--accent:#1d4ed8}
*{box-sizing:border-box}body{margin:0;background:#f1f5f9;color:var(--ink);font:16px/1.55 system-ui}
header,main,nav{max-width:1180px;margin:auto;padding:1.2rem 2rem}header{padding-top:3rem}
h1{font-size:2.3rem;margin:.2rem 0}h2{margin-top:0}a{color:var(--accent);overflow-wrap:anywhere}
nav{position:sticky;top:0;z-index:2;background:#fff;border-bottom:1px solid var(--line);display:flex;gap:1rem;flex-wrap:wrap}
section{scroll-margin-top:8rem;margin:1.5rem 0}article,.panel{background:white;border:1px solid var(--line);border-radius:12px;padding:1.4rem;margin:1rem 0}
.cards{display:flex;gap:.8rem;flex-wrap:wrap}.metric{background:#fff;border:1px solid var(--line);border-radius:10px;padding:1rem;min-width:140px}.metric strong{display:block;font-size:1.8rem}
.badge{display:inline-block;border:1px solid #64748b;border-radius:2rem;padding:.15rem .7rem;margin:.15rem;color:#172b43;background:#e2e8f0}
.warning{border-left:5px solid #9a3412;padding:1rem;background:#fff7ed;color:#7c2d12}
dl{display:grid;grid-template-columns:minmax(9rem,24%) 1fr;gap:.4rem 1rem}dt{font-weight:600}dd{margin:0;min-width:0;overflow-wrap:anywhere}
li{margin:.6rem 0}pre,code{white-space:pre-wrap;overflow-wrap:anywhere}small,.muted{color:var(--muted)}
details{border-top:1px solid var(--line);margin:.8rem 0;padding:.5rem 0}summary{cursor:pointer;font-weight:600}
input,select{font:inherit;padding:.55rem;border:1px solid #64748b;border-radius:6px;max-width:100%}
.controls{display:flex;flex-wrap:wrap;gap:1rem}.controls label{display:grid;gap:.3rem}
:focus-visible{outline:3px solid #9a3412;outline-offset:4px}[hidden]{display:none!important}
.skip{position:absolute;left:-9999px}.skip:focus{left:1rem;top:1rem;background:white;padding:1rem}
@media(max-width:700px){header,main,nav{padding:1rem}dl{grid-template-columns:1fr}dd{margin-bottom:.7rem}h1{font-size:1.8rem}nav{position:static}}
@media print{nav,.controls{display:none}body{background:white}article{break-inside:avoid}}
"""
JS = """
(() => {
 const search=document.getElementById('search'), status=document.getElementById('status-filter');
 const review=document.getElementById('review-filter'), cards=[...document.querySelectorAll('[data-case]')];
 const fold=x=>x.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLocaleLowerCase();
 const update=()=>{let count=0;for(const card of cards){
  const show=fold(card.textContent).includes(fold(search.value)) && (!status.value||card.dataset.status===status.value)
    && (!review.value||card.dataset.review===review.value);card.hidden=!show;if(show)count++;
 } document.getElementById('visible-count').textContent=String(count);};
 [search,status,review].forEach(x=>x.addEventListener('input',update));
 document.querySelectorAll('a[href^="#"]').forEach(a=>a.addEventListener('click',()=>{
  const target=document.getElementById(a.hash.slice(1));if(!target)return;
  for(let p=target;p;p=p.parentElement){if(p.tagName==='DETAILS')p.open=true;if(p.hasAttribute('data-case'))p.hidden=false;}
 }));update();
})();
"""


def review_html(
    data: dict[str, object],
    *,
    language: str,
    title: str,
    accent: str,
    density: str,
    context: ReviewContext | None = None,
) -> str:
    def esc(value: object) -> str:
        return html.escape(str(value), quote=True)

    def label(value: str) -> str:
        if value == "used_by" and language != "pt-BR":
            return "Used by:"
        return PT.get(value, value) if language == "pt-BR" else value.replace("_", " ")

    def items(value: object) -> list[dict[str, object]]:
        return [dict(x) for x in value if isinstance(x, Mapping)] if isinstance(value, list) else []

    def anchor(identifier: str) -> str:
        return "ref-" + hashlib.sha256(identifier.encode()).hexdigest()[:24]

    records: dict[str, dict[str, object]] = {}

    def index(value: object) -> None:
        if isinstance(value, dict):
            if "id" in value and len(set(value) - {"id", "project_id", "snapshot_id"}) > 0:
                records.setdefault(str(value["id"]), value)
            for child in value.values():
                index(child)
        elif isinstance(value, list):
            for child in value:
                index(child)

    index(data)
    context_data = context.model_dump(mode="json") if context else {}
    index(context_data)

    def value_html(value: object, field: str = "") -> str:
        if value is None:
            return f'<span class="muted">{esc(label("Not supplied"))}</span>'
        if isinstance(value, bool):
            return ("Sim" if value else "Não") if language == "pt-BR" else str(value)
        if isinstance(value, dict):
            if set(value) <= {"id", "project_id", "snapshot_id"} and "id" in value:
                identifier = str(value["id"])
                if any(item.get("id") == identifier for item in items(data.get("cases"))):
                    return f'<a href="#case-{esc(identifier)}">{esc(identifier)}</a>'
                for collection, prefix in (("shared_steps", "shared"), ("parameters", "parameter")):
                    if any(item.get("id") == identifier for item in items(data.get(collection))):
                        return f'<a href="#{prefix}-{esc(identifier)}">{esc(identifier)}</a>'
                if identifier in records:
                    return f'<a href="#{anchor(identifier)}">{esc(identifier)}</a>'
                return f"<code>{esc(identifier)}</code> <small>({esc(label('Reference unavailable'))})</small>"
            return fields(value)
        if isinstance(value, list):
            return "<ol>" + "".join(f"<li>{value_html(x, field)}</li>" for x in value) + "</ol>"
        rendered = localize_presentation_text(str(value), field, language)
        return esc(rendered)

    def fields(record: dict[str, object]) -> str:
        visible: list[str] = []
        technical: list[str] = []
        for key, value in record.items():
            if value == [] or value == {}:
                continue
            row = f"<dt>{esc(label(key))}</dt><dd>{value_html(value, key)}</dd>"
            (technical if key in TECHNICAL or key.endswith("_hash") else visible).append(row)
        details = (
            (
                f"<details><summary>{esc(label('Technical details'))}</summary><dl>"
                + "".join(technical)
                + "</dl></details>"
            )
            if technical
            else ""
        )
        return "<dl>" + "".join(visible) + "</dl>" + details

    cases = items(data.get("cases"))
    sections: list[tuple[str, str, str]] = []
    metrics = [("Test Cases", len(cases))]
    metrics += [
        (state, sum(c.get("readiness") == state for c in cases))
        for state in ("READY", "BLOCKED_SOURCE", "READY_WITH_REVIEW")
    ]
    overview = (
        '<div class="cards">'
        + "".join(
            f'<div class="metric"><strong>{count}</strong>{esc(label(name))}</div>'
            for name, count in metrics
        )
        + "</div>"
    )
    overview += f"<p>{esc(label('Status'))}: {value_html(data.get('status'), 'status')} · <code>{esc(data.get('mode'))}</code></p>"
    overview += f"<p>{esc(label('Proposal only; history unchanged.'))}</p>"
    if not context:
        overview += f'<p class="warning">{esc(label("Context not supplied; source traceability is incomplete."))}</p>'
    sections.append(("overview", "Overview", overview))

    def options(key: str) -> str:
        return f'<option value="">{esc(label("All"))}</option>' + "".join(
            f'<option value="{esc(x)}">{esc(label(x))}</option>'
            for x in sorted({str(case.get(key, "")) for case in cases})
        )

    controls = (
        f'<div class="controls"><label>{esc(label("Search"))}<input id="search" type="search"></label>'
        f'<label>{esc(label("Status"))}<select id="status-filter">{options("readiness")}</select></label>'
        f'<label>{esc(label("Review"))}<select id="review-filter">{options("review_status")}</select></label></div>'
        f'<p aria-live="polite">{esc(label("Visible cases"))}: <span id="visible-count">{len(cases)}</span></p>'
    )
    case_html = ""
    for case in cases:
        case_html += (
            f'<article id="case-{esc(case.get("id"))}" data-case '
            f'data-status="{esc(case.get("readiness"))}" data-review="{esc(case.get("review_status"))}">'
            f'<h3>{esc(case.get("title"))}</h3><span class="badge">{value_html(case.get("readiness"), "readiness")}</span>'
            + fields(case)
            + "</article>"
        )
    sections.append(("cases", "Test Cases", controls + case_html))
    for key, name, prefix in (
        ("shared_steps", "Shared Steps", "shared"),
        ("parameters", "parameters", "parameter"),
        ("revisions", "Reviews", "changes"),
        ("traceability", "Traceability", "trace"),
    ):
        group = items(data.get(key))
        if group:
            body = "".join(
                f'<article id="{prefix}-{esc(x.get("id"))}">{fields(x)}</article>' for x in group
            )
            if key == "revisions":
                body = (
                    f"<p>{esc(label('Original'))} / {esc(label('Proposed'))} — {esc(label('Historical asset modified? NO'))}</p>"
                    + body
                )
            sections.append((prefix if prefix != "parameter" else "parameters", name, body))
    if context:
        for kind, name in (("requirement", "Requirements"), ("atomic_criterion", "Criteria")):
            nodes = [x for x in context.project_model.nodes if x.kind == kind]
            if nodes:
                sections.append(
                    (
                        kind,
                        name,
                        "".join(
                            "<article>" + fields(x.model_dump(mode="json")) + "</article>"
                            for x in nodes
                        ),
                    )
                )
        for key, name in (("risks", "Risks"), ("scenarios", "Scenarios"), ("findings", "Gaps")):
            analysis_records = getattr(context.analysis, key)
            if analysis_records:
                sections.append(
                    (
                        key,
                        name,
                        "".join(
                            "<article>" + fields(x.model_dump(mode="json")) + "</article>"
                            for x in analysis_records
                        ),
                    )
                )
        if context.relations:
            body = f'<p class="warning">{esc(label("Candidate relations; no normative winner or approval."))}</p>'
            for edge, decision in zip(
                context.relations.relations, context.relations.adjudications, strict=True
            ):
                body += (
                    "<article>"
                    + fields(edge.model_dump(mode="json"))
                    + fields(decision.model_dump(mode="json"))
                )
                if decision.human_review_required:
                    body += f'<p class="warning">{esc(label("Normative promotion blocked; affected tests not linked by H4."))}</p>'
                body += "</article>"
            sections.append(("conflicts", "Conflicts", body))
    gaps = data.get("limitations")
    if gaps:
        sections.append(("limitations", "Gaps", value_html(gaps)))
    # Every emitted reference has one stable target, including nested source/oracle/claim records.
    evidence = "".join(
        f'<details id="{anchor(identifier)}"><summary>{esc(identifier)}</summary>{fields(record)}</details>'
        for identifier, record in sorted(records.items())
    )
    sections.append(("evidence", "Evidence", evidence))
    nav = "".join(f'<a href="#{key}">{esc(label(name))}</a>' for key, name, _ in sections)
    body = "".join(
        f'<section id="{key}"><h2>{esc(label(name))}</h2>{content}</section>'
        for key, name, content in sections
    )
    return (
        '<!doctype html><html lang="' + esc(language) + '"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{esc(title)}</title><style>{CSS}:root{{--accent:{accent}}}</style></head>"
        f'<body data-density="{esc(density)}"><a class="skip" href="#main">{esc(label("Test Cases"))}</a>'
        f"<header><small>QE Engineering · Technical Preview</small><h1>{esc(title)}</h1>"
        f"<small>{esc(data.get('project_id'))} / {esc(data.get('snapshot_id'))}</small></header>"
        f'<nav aria-label="{esc(label("Overview"))}">{nav}</nav><main id="main">{body}</main>'
        f'<script type="text/javascript">{JS}</script></body></html>\n'
    )
