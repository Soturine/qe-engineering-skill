"""Small locale catalog for engine-owned text.

Evidence, oracle statements, paths, identifiers, and user-authored text must never pass through
this module.  It is intentionally an exact-message catalog rather than a general translator.
"""

from __future__ import annotations

import re

from qe_skill import domain as d

ENGINE_PT: dict[str, str] = {
    "The source claim is missing or outside the current project snapshot.": (
        "A afirmação de origem está ausente ou fora do snapshot atual do projeto."
    ),
    "The current claim does not pass provenance validation.": (
        "A afirmação atual não passa na validação de proveniência."
    ),
    "Expected Result text must exactly preserve the supporting claim.": (
        "O texto do Resultado Esperado deve preservar exatamente a afirmação de suporte."
    ),
    "The candidate oracle did not pass the repository trust validator.": (
        "O oráculo candidato não passou no validador de confiança do repositório."
    ),
    "Oracle semantics exactly preserve the validated current claim.": (
        "A semântica do oráculo preserva exatamente a afirmação atual validada."
    ),
    "Oracle reuse requires an oracle in the exact current project snapshot.": (
        "A reutilização exige um oráculo no snapshot atual exato do projeto."
    ),
    "The existing oracle does not pass current provenance validation.": (
        "O oráculo existente não passa na validação atual de proveniência."
    ),
    "The existing oracle is current and passes provenance validation.": (
        "O oráculo existente é atual e passa na validação de proveniência."
    ),
    "A canonical concept lacks literal support in cited evidence.": (
        "Um conceito canônico não possui suporte literal na evidência citada."
    ),
    "A canonical label differs from source wording without an alias relation.": (
        "Um rótulo canônico difere do texto-fonte sem uma relação de alias."
    ),
    "A normalized constraint lacks literal evidence.": (
        "Uma restrição normalizada não possui evidência literal."
    ),
    "An alias relation lacks literal evidence.": (
        "Uma relação de alias não possui evidência literal."
    ),
    "Candidate evidence is not bound to this reasoning request.": (
        "A evidência candidata não está vinculada a esta solicitação de raciocínio."
    ),
    "Candidate has no typed normalization proposal.": (
        "O candidato não possui proposta de normalização tipada."
    ),
    "Candidate normalization does not satisfy the typed contract.": (
        "A normalização candidata não satisfaz o contrato tipado."
    ),
    "Candidate evidence is absent from the reasoning request.": (
        "A evidência candidata está ausente da solicitação de raciocínio."
    ),
    "Normalized modality conflicts with an explicit source marker.": (
        "A modalidade normalizada conflita com um marcador explícito da fonte."
    ),
    "Normalized meaning loses explicit source negation.": (
        "O significado normalizado perde uma negação explícita da fonte."
    ),
    "Normalized constraint direction conflicts with an explicit source marker.": (
        "A direção da restrição normalizada conflita com um marcador explícito da fonte."
    ),
    "No validated exact supporting claim is available.": (
        "Nenhuma afirmação de suporte exata e validada está disponível."
    ),
    "Operational path is partial or unresolved; no remainder was invented.": (
        "O caminho operacional está parcial ou não resolvido; nenhum trecho restante foi inventado."
    ),
    "Record the observed result if this step cannot be completed.": (
        "Registre o resultado observado se este passo não puder ser concluído."
    ),
    "No operational path supports this action.": (
        "Nenhum caminho operacional oferece suporte a esta ação."
    ),
    "No verified operational path supports this action.": (
        "Nenhum caminho operacional verificado oferece suporte a esta ação."
    ),
    "For a normal Pass, record the observation at the validating step.": (
        "Para uma aprovação normal, registre a observação no passo de validação."
    ),
    "For Fail or Blocked, record the affected step and diagnostic observation.": (
        "Para Falha ou Bloqueio, registre o passo afetado e a observação diagnóstica."
    ),
    "Record the observed result for any Fail or Blocked outcome.": (
        "Registre o resultado observado para qualquer resultado de Falha ou Bloqueio."
    ),
    (
        "For this explicitly modeled high-consequence risk, retain the environment/build, "
        "actor, inputs, affected step, timestamp, and relevant diagnostic observations."
    ): (
        "Para este risco de alta consequência modelado explicitamente, preserve ambiente/build, "
        "ator, entradas, passo afetado, timestamp e observações diagnósticas relevantes."
    ),
    "Record the step outcome; on Fail or Blocked retain context sufficient to reproduce it.": (
        "Registre o resultado do passo; em caso de Falha ou Bloqueio, preserve contexto suficiente "
        "para reproduzi-lo."
    ),
    "Record the observation for any Fail or Blocked result.": (
        "Registre a observação para qualquer resultado de Falha ou Bloqueio."
    ),
    "No defensible normative oracle is available.": (
        "Nenhum oráculo normativo defensável está disponível."
    ),
    "Environment evidence is not available.": "A evidência de ambiente não está disponível.",
    "Cleanup evidence is not available.": "A evidência de limpeza não está disponível.",
    "Isolation evidence is not available.": "A evidência de isolamento não está disponível.",
    "Build or version context is not available.": (
        "O contexto de build ou versão não está disponível."
    ),
    "Actor/profile evidence is not available.": ("A evidência de ator/perfil não está disponível."),
    "Actor profile context is not available.": (
        "O contexto de perfil do ator não está disponível."
    ),
    "Concrete preparation remains operator-supplied; no value was invented.": (
        "A preparação concreta continua a cargo do operador; nenhum valor foi inventado."
    ),
    "Strict READY validation requires additional supported context.": (
        "A validação estrita de PRONTO exige contexto adicional com suporte."
    ),
    "All required steps satisfy their cited oracles.": (
        "Todos os passos obrigatórios satisfazem os oráculos citados."
    ),
    "A required observation contradicts its cited oracle.": (
        "Uma observação obrigatória contradiz o oráculo citado."
    ),
    "Required evidence, preparation, action, or observation cannot be completed.": (
        "A evidência, preparação, ação ou observação obrigatória não pode ser concluída."
    ),
    "Generated from an explicitly selected M2 scenario without adding behavior.": (
        "Gerado a partir de um cenário M2 explicitamente selecionado, sem adicionar comportamento."
    ),
    "Explicit criterion dimensions form a bounded scenario candidate.": (
        "As dimensões explícitas do critério formam um cenário candidato limitado."
    ),
    "Partition is explicitly declared by a referenced constraint.": (
        "A partição é declarada explicitamente por uma restrição referenciada."
    ),
    "Candidate value is adjacent to an explicit numeric limit.": (
        "O valor candidato é adjacente a um limite numérico explícito."
    ),
    "Scenario reflects an explicit modeled transition; no invalid outcome is inferred.": (
        "O cenário reflete uma transição modelada explícita; nenhum resultado inválido é inferido."
    ),
    "Scenario reflects an explicit structured condition/outcome rule.": (
        "O cenário reflete uma regra estruturada explícita de condição e resultado."
    ),
    "An explicitly modeled risk activates only its named category; no outcome is invented.": (
        "Um risco modelado explicitamente ativa somente sua categoria; "
        "nenhum resultado é inventado."
    ),
    "No selected M2 scenarios were available.": (
        "Nenhum cenário M2 selecionado estava disponível."
    ),
    "The same evidence-backed preparation is repeated across proposals.": (
        "A mesma preparação sustentada por evidência se repete entre propostas."
    ),
    "The same verified preparation/navigation prefix is repeated.": (
        "O mesmo prefixo verificado de preparação/navegação se repete."
    ),
    "Explicit evidence-backed test data can be supplied as a parameter.": (
        "Dados de teste explícitos e sustentados por evidência podem ser fornecidos como parâmetro."
    ),
    "Historical data is missing a partition or is explicitly hard-coded.": (
        "Os dados históricos não possuem partição ou estão explicitamente fixos."
    ),
    "Historical procedure has no verified path.": (
        "O procedimento histórico não possui caminho verificado."
    ),
    "Historical Expected Result has no oracle reference.": (
        "O Resultado Esperado histórico não possui referência de oráculo."
    ),
    (
        "Use the proposed evidence-backed procedure only after its readiness gate; "
        "the historical procedure remains unchanged."
    ): (
        "Use o procedimento proposto sustentado por evidência somente após seu gate de prontidão; "
        "o procedimento histórico permanece inalterado."
    ),
    (
        "Split explicitly grouped independent validations into diagnosable oracle-backed steps; "
        "do not normalize unsupported assertions."
    ): (
        "Separe validações independentes agrupadas explicitamente em passos diagnosticáveis "
        "sustentados por oráculos; não normalize afirmações sem suporte."
    ),
    "One or more source assumptions do not resolve in destination evidence.": (
        "Uma ou mais premissas de origem não são resolvidas pela evidência de destino."
    ),
    "Source assumptions are not bound to the destination project snapshot.": (
        "As premissas de origem não estão vinculadas ao snapshot do projeto de destino."
    ),
    "The source-project oracle is not normative in the destination.": (
        "O oráculo do projeto de origem não é normativo no destino."
    ),
    "Destination path, actor, or oracle assumptions are incomplete.": (
        "As premissas de caminho, ator ou oráculo do destino estão incompletas."
    ),
    "The destination operational path is not verified.": (
        "O caminho operacional de destino não está verificado."
    ),
    "All modeled assumptions resolve in current destination evidence.": (
        "Todas as premissas modeladas são resolvidas pela evidência atual de destino."
    ),
}


def resolve_output_language(
    project_locale: d.LanguageCode, output_language: d.OutputLanguage
) -> d.OutputLanguage:
    """Resolve the presentation language without changing source language or authority."""

    if output_language != "source":
        return output_language
    return "pt-BR" if project_locale == "pt-BR" else "en"


def localize_engine_text(value: str, language: d.OutputLanguage) -> str:
    """Localize only known engine-owned text; unknown values remain literal."""

    if language != "pt-BR":
        return value
    exact = ENGINE_PT.get(value)
    if exact is not None:
        return exact
    match = re.fullmatch(r"Review scenario (.+)", value)
    if match:
        return f"Revisar cenário {match.group(1)}"
    match = re.fullmatch(r"Partition: (.+)", value)
    if match:
        return f"Partição: {match.group(1)}"
    if value == "Explicit boundary candidate":
        return "Candidato de limite explícito"
    match = re.fullmatch(r"Prepare: (.+)", value)
    if match:
        return f"Preparar: {match.group(1)}"
    match = re.fullmatch(r"Reusable setup for (.+)", value)
    if match:
        return f"Preparação reutilizável para {match.group(1)}"
    return value
