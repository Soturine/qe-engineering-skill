"""Grounded semantic normalization for M4.H3.

Normalization makes candidate meanings comparable without replacing their source wording or
promoting them into Project Model facts. Provider-produced structure remains review material.
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from typing import Literal

from pydantic import Field, JsonValue, ValidationError, model_validator

from qe_skill import domain as d
from qe_skill.reasoning import (
    ProviderIdentity,
    ReasoningRequest,
    ReasoningResult,
    canonical_hash,
)
from qe_skill.semantic import (
    CandidateEvidence,
    SemanticCandidate,
    SemanticCandidateSet,
    validate_candidate_set,
)
from qe_skill.validation import Result, same_scope

RecordKind = Literal["FACT", "OBSERVATION", "CLAIM", "HYPOTHESIS", "DECISION", "ORACLE"]
Modality = Literal["MUST", "MUST_NOT", "SHOULD", "MAY", "OPTIONAL", "CONDITIONAL", "UNSPECIFIED"]
Polarity = Literal["POSITIVE", "NEGATIVE", "UNSPECIFIED"]
NormalizationStatus = Literal[
    "NOT_REQUESTED", "COMPLETE", "PARTIAL", "BLOCKED", "STALE_INPUT", "REJECTED"
]
GroundingCode = Literal["GROUNDING_MISSING", "ALIAS_RELATION_MISSING"]


class GroundedConcept(d.Record):
    """Canonical candidate label grounded by literal forms in cited excerpts."""

    label: d.Text
    surface_forms: list[d.Text] = Field(min_length=1)
    evidence: list[d.Ref] = Field(min_length=1)


class GroundedTerm(GroundedConcept):
    role: Literal["ENTITY", "STATE", "FIELD", "VALUE", "ACTION", "TECHNICAL_IDENTIFIER", "OTHER"]


class AliasRelation(d.Record):
    """An explicit relation; normalization never overwrites the source form."""

    alias: d.Text
    canonical_label: d.Text
    evidence: list[d.Ref] = Field(min_length=1)


class MeaningConstraint(d.Record):
    kind: d.Text
    operator: Literal["EQ", "NE", "LT", "LE", "GT", "GE", "IN", "MATCHES", "OTHER"]
    value: JsonValue
    unit: d.Text | None = None
    surface_form: d.Text
    evidence: list[d.Ref] = Field(min_length=1)


class SemanticMeaning(d.Record):
    record_kind: RecordKind
    actor: GroundedConcept | None = None
    capability: GroundedConcept | None = None
    intent: GroundedConcept | None = None
    modality: Modality = "UNSPECIFIED"
    polarity: Polarity = "UNSPECIFIED"
    constraints: list[MeaningConstraint] = Field(default_factory=list)
    aliases: list[AliasRelation] = Field(default_factory=list)
    terms: list[GroundedTerm] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_meaning(self) -> SemanticMeaning:
        if not any((self.actor, self.capability, self.intent, self.constraints, self.terms)):
            raise ValueError("normalized meaning requires a grounded semantic component")
        return self


class OriginalStatement(d.Record):
    excerpt: d.Ref
    source: d.Ref
    source_hash: d.Digest
    location: d.Text
    span: d.Ref | None = None
    text: d.Text
    source_language: d.LanguageCode
    language_method: Literal["DECLARED", "BOUNDED", "UNDETERMINED"]
    language_confidence: Literal["HIGH", "LOW"]
    authority_class: Literal[
        "CONTRACT",
        "TECHNICAL_CONTRACT",
        "ORGANIZATIONAL_POLICY",
        "IMPLEMENTATION",
        "HISTORICAL",
        "GUIDANCE",
    ]
    source_lifecycle: Literal[
        "draft", "approved", "active", "superseded", "deprecated", "archived", "unknown"
    ]


class GherkinMarker(d.Record):
    line: int = Field(ge=1)
    keyword: d.Text
    role: Literal[
        "FEATURE", "SCENARIO", "BACKGROUND", "GIVEN", "WHEN", "THEN", "AND", "BUT", "EXAMPLES"
    ]
    language: Literal["pt-BR", "en"]


class SurfaceGuards(d.Record):
    """Deterministic distinctions that a probabilistic interpretation cannot erase."""

    observed_modality: Modality = "UNSPECIFIED"
    observed_polarity: Polarity = "UNSPECIFIED"
    numeric_literals: list[d.Text] = Field(default_factory=list)
    gherkin_markers: list[GherkinMarker] = Field(default_factory=list)


class NormalizationIssue(d.Record):
    candidate: d.Ref
    code: Literal[
        "NORMALIZATION_MISSING",
        "NORMALIZATION_INVALID",
        "GROUNDING_MISSING",
        "ALIAS_RELATION_MISSING",
        "MODALITY_MISMATCH",
        "NEGATION_LOST",
    ]
    message: d.Text


class NormalizedSemanticRecord(d.Artifact):
    candidate: d.Ref
    candidate_hash: d.Digest
    candidate_statement: d.Text | None = None
    original_statements: list[OriginalStatement] = Field(min_length=1)
    meaning: SemanticMeaning
    surface_guards: SurfaceGuards
    comparison_key: d.Digest
    interpretation: Literal["explicit", "structural", "heuristic", "inferred", "unresolved"]
    confidence: float = Field(ge=0, le=1)
    inferred: bool
    producer: Literal["DETERMINISTIC", "HEURISTIC", "PROVIDER"]
    provider_identity: ProviderIdentity | None = None
    prompt_version: d.Text
    configuration_hash: d.Digest
    extractor_version: d.Text
    run_id: d.Text
    review_state: Literal["PENDING_REVIEW", "REVIEW_REQUIRED", "BLOCKED_SOURCE"]
    normative: Literal[False] = False
    authority_promoted: Literal[False] = False


class SemanticNormalizationSet(d.Artifact):
    candidate_set: d.Ref
    candidate_set_hash: d.Digest
    status: NormalizationStatus
    records: list[NormalizedSemanticRecord]
    issues: list[NormalizationIssue] = Field(default_factory=list)
    project_locale: d.LanguageCode = "und"
    output_language: d.OutputLanguage = "source"
    external_writes: Literal[False] = False
    authority_changed: Literal[False] = False


_MODAL_PATTERNS: tuple[tuple[Modality, re.Pattern[str]], ...] = (
    (
        "MUST_NOT",
        re.compile(
            r"\b(?:must\s+not|shall\s+not|mustn't|n[aã]o\s+(?:pode|deve|dever[aá])|"
            r"n[aã]o\s+ser[aá]|é\s+proibido|n[aã]o\s+é\s+permitido)\b",
            re.I,
        ),
    ),
    (
        "MUST",
        re.compile(
            r"\b(?:must(?!\s+not)|shall(?!\s+not)|is\s+required\s+to|"
            r"(?<!não\s)(?<!nao\s)deve|dever[aá]|precisa|é\s+obrigat[oó]rio|"
            r"é\s+necess[aá]rio|tem\s+que)\b",
            re.I,
        ),
    ),
    (
        "SHOULD",
        re.compile(r"\b(?:should|deveria|recomenda-se|preferencialmente|é\s+recomendado)\b", re.I),
    ),
    ("OPTIONAL", re.compile(r"\b(?:is\s+optional|opcional)\b", re.I)),
    (
        "CONDITIONAL",
        re.compile(
            r"\b(?:quando\s+aplic[aá]vel|se\s+dispon[ií]vel|caso\s+exista|se\s+configurado)\b",
            re.I,
        ),
    ),
    ("MAY", re.compile(r"\b(?:may|pode|poder[aá]|é\s+permitido)\b", re.I)),
)
_NEGATION = re.compile(r"\b(?:not|never|without|n[aã]o|nunca|jamais|sem)\b", re.I)
_NUMBER = re.compile(
    r"(?<![\w.])-?\d{1,3}(?:\.\d{3})+(?:,\d+)?(?!\w)|"
    r"(?<![\w.])-?\d+(?:[.,]\d+)?(?!\w)"
)
_PT_HINTS = frozenset(
    {
        "usuário",
        "cliente",
        "pedido",
        "deve",
        "pode",
        "quando",
        "então",
        "dado",
        "após",
        "até",
        "recebe",
        "possui",
        "retornar",
        "obrigatório",
        "opcional",
        "endereço",
        "sistema",
    }
)
_EN_HINTS = frozenset(
    {"user", "customer", "order", "must", "may", "when", "then", "given", "after", "within"}
)
_TECHNICAL_EN = re.compile(
    r"(?:/[A-Za-z0-9_./{}-]+|\b(?:GET|POST|PUT|PATCH|DELETE)\b|\b[a-z]+_[a-z0-9_]+\b)"
)
_GHERKIN: tuple[tuple[str, str, str], ...] = (
    ("Esquema do Cenário", "SCENARIO", "pt-BR"),
    ("Funcionalidade", "FEATURE", "pt-BR"),
    ("Cenário", "SCENARIO", "pt-BR"),
    ("Contexto", "BACKGROUND", "pt-BR"),
    ("Exemplos", "EXAMPLES", "pt-BR"),
    ("Dado", "GIVEN", "pt-BR"),
    ("Dada", "GIVEN", "pt-BR"),
    ("Dados", "GIVEN", "pt-BR"),
    ("Dadas", "GIVEN", "pt-BR"),
    ("Quando", "WHEN", "pt-BR"),
    ("Então", "THEN", "pt-BR"),
    ("E", "AND", "pt-BR"),
    ("Mas", "BUT", "pt-BR"),
    ("Scenario Outline", "SCENARIO", "en"),
    ("Feature", "FEATURE", "en"),
    ("Scenario", "SCENARIO", "en"),
    ("Background", "BACKGROUND", "en"),
    ("Examples", "EXAMPLES", "en"),
    ("Given", "GIVEN", "en"),
    ("When", "WHEN", "en"),
    ("Then", "THEN", "en"),
    ("And", "AND", "en"),
    ("But", "BUT", "en"),
)


def _compare_text(value: str) -> str:
    """NFC/casefold is comparison-only; evidence remains byte-for-byte unchanged."""

    return unicodedata.normalize("NFC", value).casefold()


def detect_source_language(text: str) -> tuple[d.LanguageCode, Literal["HIGH", "LOW"]]:
    """Small, non-authoritative detector for pt-BR/en/mixed; uncertainty remains explicit."""

    normalized = _compare_text(text)
    words = set(re.findall(r"[^\W\d_]+", normalized, flags=re.UNICODE))
    pt_score = len(words & _PT_HINTS)
    en_score = len(words & _EN_HINTS)
    technical_english = bool(_TECHNICAL_EN.search(text))
    if pt_score >= 2 and (en_score >= 2 or technical_english):
        return "mixed", "HIGH"
    if pt_score >= 2 and pt_score > en_score:
        return "pt-BR", "HIGH"
    if en_score >= 2 and en_score > pt_score:
        return "en", "HIGH"
    return "und", "LOW"


def _gherkin_markers(text: str) -> list[GherkinMarker]:
    markers: list[GherkinMarker] = []
    for number, line in enumerate(text.splitlines(), start=1):
        content = line.strip()
        for keyword, role, language in _GHERKIN:
            if re.match(rf"^{re.escape(keyword)}(?:\s|:|$)", content, re.I):
                markers.append(
                    GherkinMarker.model_validate(
                        {"line": number, "keyword": keyword, "role": role, "language": language}
                    )
                )
                break
    return markers


def _surface_guards(statements: list[OriginalStatement]) -> SurfaceGuards:
    text = "\n".join(item.text for item in statements)
    observed = [modality for modality, pattern in _MODAL_PATTERNS if pattern.search(text)]
    modality: Modality
    if "MUST_NOT" in observed:
        modality = "MUST_NOT"
    else:
        modality = observed[0] if len(set(observed)) == 1 else "UNSPECIFIED"
    polarity: Polarity = "NEGATIVE" if _NEGATION.search(text) else "UNSPECIFIED"
    # Preserve locale punctuation; constraints may carry a canonical numeric value separately.
    numbers = sorted({match.group(0) for match in _NUMBER.finditer(text)})
    return SurfaceGuards(
        observed_modality=modality,
        observed_polarity=polarity,
        numeric_literals=numbers,
        gherkin_markers=[marker for item in statements for marker in _gherkin_markers(item.text)],
    )


def _comparison_key(meaning: SemanticMeaning, guards: SurfaceGuards) -> str:
    def concept(value: GroundedConcept | None) -> str | None:
        return _compare_text(value.label) if value else None

    payload = {
        "record_kind": meaning.record_kind,
        "actor": concept(meaning.actor),
        "capability": concept(meaning.capability),
        "intent": concept(meaning.intent),
        "modality": meaning.modality,
        "polarity": meaning.polarity,
        "constraints": sorted(
            [
                {
                    "kind": item.kind.casefold(),
                    "operator": item.operator,
                    "value": item.value,
                    "unit": _compare_text(item.unit) if item.unit else None,
                }
                for item in meaning.constraints
            ],
            key=lambda item: json.dumps(item, sort_keys=True, ensure_ascii=False),
        ),
        "numeric_literals": guards.numeric_literals,
        "terms": sorted([(item.role, _compare_text(item.label)) for item in meaning.terms]),
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
    )
    return hashlib.sha256(encoded.encode()).hexdigest()


def _statement(evidence: CandidateEvidence, request: ReasoningRequest) -> OriginalStatement:
    excerpt = next(item for item in request.excerpts if item.id == evidence.excerpt.id)
    detected, confidence = detect_source_language(excerpt.text)
    language = excerpt.source_language if excerpt.source_language != "und" else detected
    method: Literal["DECLARED", "BOUNDED", "UNDETERMINED"] = (
        "DECLARED" if excerpt.source_language != "und" else "BOUNDED"
    )
    if language == "und":
        method = "UNDETERMINED"
    return OriginalStatement(
        excerpt=evidence.excerpt.model_copy(deep=True),
        source=evidence.source.model_copy(deep=True),
        source_hash=evidence.source_hash,
        location=evidence.location,
        span=evidence.span.model_copy(deep=True) if evidence.span else None,
        text=excerpt.text,
        source_language=language,
        language_method=method,
        language_confidence="HIGH" if excerpt.source_language != "und" else confidence,
        authority_class=evidence.authority_class,
        source_lifecycle=evidence.source_lifecycle,
    )


def _grounding_issue(
    candidate: SemanticCandidate,
    meaning: SemanticMeaning,
    excerpts: dict[str, str],
) -> tuple[GroundingCode, str] | None:
    concepts = [
        item for item in (meaning.actor, meaning.capability, meaning.intent, *meaning.terms) if item
    ]
    for concept in concepts:
        known = [
            ref for ref in concept.evidence if ref.id in excerpts and same_scope(ref, candidate)
        ]
        if len(known) != len(concept.evidence) or any(
            not any(_compare_text(form) in _compare_text(excerpts[ref.id]) for ref in known)
            for form in concept.surface_forms
        ):
            return (
                "GROUNDING_MISSING",
                "A canonical concept lacks literal support in cited evidence.",
            )
        if _compare_text(concept.label) not in {
            _compare_text(form) for form in concept.surface_forms
        }:
            related = any(
                _compare_text(alias.canonical_label) == _compare_text(concept.label)
                and _compare_text(alias.alias)
                in {_compare_text(form) for form in concept.surface_forms}
                for alias in meaning.aliases
            )
            if not related:
                return (
                    "ALIAS_RELATION_MISSING",
                    "A canonical label differs from source wording without an alias relation.",
                )
    for item in meaning.constraints:
        known = [ref for ref in item.evidence if ref.id in excerpts and same_scope(ref, candidate)]
        if len(known) != len(item.evidence) or not any(
            _compare_text(item.surface_form) in _compare_text(excerpts[ref.id]) for ref in known
        ):
            return "GROUNDING_MISSING", "A normalized constraint lacks literal evidence."
    for alias in meaning.aliases:
        known = [ref for ref in alias.evidence if ref.id in excerpts and same_scope(ref, candidate)]
        if len(known) != len(alias.evidence) or not any(
            _compare_text(alias.alias) in _compare_text(excerpts[ref.id]) for ref in known
        ):
            return "GROUNDING_MISSING", "An alias relation lacks literal evidence."
    return None


def normalize_candidate(
    candidate: SemanticCandidate, request: ReasoningRequest
) -> tuple[NormalizedSemanticRecord | None, NormalizationIssue | None]:
    """Normalize one candidate, rejecting unsupported structure without guessing."""

    candidate_ref = d.Ref(
        id=candidate.id, project_id=candidate.project_id, snapshot_id=candidate.snapshot_id
    )
    requested = {item.id: item for item in request.excerpts}
    bound = all(
        (excerpt := requested.get(item.excerpt.id)) is not None
        and excerpt.source == item.source
        and excerpt.source_hash == item.source_hash
        and excerpt.location == item.location
        and excerpt.span == item.span
        for item in candidate.evidence
    )
    if not same_scope(candidate, request) or not bound:
        return None, NormalizationIssue(
            candidate=candidate_ref,
            code="GROUNDING_MISSING",
            message="Candidate evidence is not bound to this reasoning request.",
        )
    raw = candidate.structured_value.get("normalization")
    if not isinstance(raw, dict):
        return None, NormalizationIssue(
            candidate=candidate_ref,
            code="NORMALIZATION_MISSING",
            message="Candidate has no typed normalization proposal.",
        )
    try:
        meaning = SemanticMeaning.model_validate(raw)
    except ValidationError:
        return None, NormalizationIssue(
            candidate=candidate_ref,
            code="NORMALIZATION_INVALID",
            message="Candidate normalization does not satisfy the typed contract.",
        )
    evidence_ids = {item.excerpt.id for item in candidate.evidence}
    excerpts = {key: requested[key].text for key in evidence_ids if key in requested}
    issue: tuple[GroundingCode, str] | None
    if len(excerpts) != len(evidence_ids):
        issue = ("GROUNDING_MISSING", "Candidate evidence is absent from the reasoning request.")
    else:
        issue = _grounding_issue(candidate, meaning, excerpts)
    if issue:
        return None, NormalizationIssue(
            candidate=candidate_ref,
            code=issue[0],
            message=issue[1],
        )
    statements = [_statement(item, request) for item in candidate.evidence]
    guards = _surface_guards(statements)
    if guards.observed_modality != "UNSPECIFIED" and meaning.modality != guards.observed_modality:
        return None, NormalizationIssue(
            candidate=candidate_ref,
            code="MODALITY_MISMATCH",
            message="Normalized modality conflicts with an explicit source marker.",
        )
    if guards.observed_polarity == "NEGATIVE" and meaning.polarity != "NEGATIVE":
        return None, NormalizationIssue(
            candidate=candidate_ref,
            code="NEGATION_LOST",
            message="Normalized meaning loses explicit source negation.",
        )
    candidate_hash = canonical_hash(candidate)
    identifier = hashlib.sha256(
        (candidate_hash + _comparison_key(meaning, guards)).encode()
    ).hexdigest()
    return (
        NormalizedSemanticRecord(
            id=f"semantic-normalization.{identifier[:24]}",
            project_id=candidate.project_id,
            snapshot_id=candidate.snapshot_id,
            candidate=candidate_ref,
            candidate_hash=candidate_hash,
            candidate_statement=candidate.statement,
            original_statements=statements,
            meaning=meaning,
            surface_guards=guards,
            comparison_key=_comparison_key(meaning, guards),
            interpretation=candidate.interpretation,
            confidence=candidate.confidence,
            inferred=candidate.inferred,
            producer=candidate.producer,
            provider_identity=candidate.provider_identity.model_copy(deep=True)
            if candidate.provider_identity
            else None,
            prompt_version=candidate.prompt_version,
            configuration_hash=candidate.configuration_hash,
            extractor_version=candidate.extractor_version,
            run_id=candidate.run_id,
            review_state=candidate.review_state,
        ),
        None,
    )


def normalize_candidate_set(
    candidate_set: SemanticCandidateSet,
    request: ReasoningRequest,
    result: ReasoningResult,
    ledger: d.SourceLedger,
    *,
    project_locale: d.LanguageCode | None = None,
    output_language: d.OutputLanguage | None = None,
) -> SemanticNormalizationSet:
    """Normalize a validated H2 set while preserving every rejection as a typed issue."""

    source_hash = canonical_hash(candidate_set)
    resolved_project_locale = project_locale or ledger.manifest.project_locale
    resolved_output_language = output_language or ledger.manifest.output_language
    identity = json.dumps(
        [source_hash, resolved_project_locale, resolved_output_language],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    artifact_id = f"semantic-normalizations.{hashlib.sha256(identity.encode()).hexdigest()[:24]}"

    def build(
        status: NormalizationStatus,
        records: list[NormalizedSemanticRecord] | None = None,
        issues: list[NormalizationIssue] | None = None,
    ) -> SemanticNormalizationSet:
        return SemanticNormalizationSet(
            id=artifact_id,
            project_id=candidate_set.project_id,
            snapshot_id=candidate_set.snapshot_id,
            candidate_set=d.Ref(
                id=candidate_set.id,
                project_id=candidate_set.project_id,
                snapshot_id=candidate_set.snapshot_id,
            ),
            candidate_set_hash=source_hash,
            status=status,
            records=records or [],
            issues=issues or [],
            project_locale=resolved_project_locale,
            output_language=resolved_output_language,
        )

    if not validate_candidate_set(candidate_set, request, result, ledger).valid:
        return build("REJECTED")
    if candidate_set.status == "NOT_REQUESTED":
        return build("NOT_REQUESTED")
    if candidate_set.status == "STALE_INPUT":
        return build("STALE_INPUT")
    if candidate_set.status in {"BLOCKED_PROVIDER", "REJECTED"}:
        return build("BLOCKED")
    records: list[NormalizedSemanticRecord] = []
    issues: list[NormalizationIssue] = []
    for candidate in candidate_set.candidates:
        record, issue = normalize_candidate(candidate, request)
        if record:
            records.append(record)
        if issue:
            issues.append(issue)
    status: NormalizationStatus = (
        "COMPLETE"
        if records and not issues and candidate_set.status == "READY_FOR_REVIEW"
        else "PARTIAL"
    )
    if not records:
        status = "REJECTED"
    return build(status, records, issues)


def validate_normalization_set(
    artifact: SemanticNormalizationSet,
    candidate_set: SemanticCandidateSet,
    request: ReasoningRequest,
    result_record: ReasoningResult,
    ledger: d.SourceLedger,
) -> Result:
    validation = Result()
    if not same_scope(artifact, candidate_set):
        validation.add("NORM_SCOPE", artifact, "Normalization crosses project or snapshot scope.")
        return validation
    expected = normalize_candidate_set(
        candidate_set,
        request,
        result_record,
        ledger,
        project_locale=artifact.project_locale,
        output_language=artifact.output_language,
    )
    if artifact != expected:
        validation.add(
            "NORM_BINDING",
            artifact,
            "Normalization content or source binding does not match deterministic reconstruction.",
        )
    return validation
