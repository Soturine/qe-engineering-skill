"""Structured clarification questions derived from rejected semantic candidates."""

from __future__ import annotations

import hashlib
import json
from typing import Literal

from pydantic import Field, model_validator

from qe_skill import domain as d
from qe_skill.localization import resolve_output_language
from qe_skill.normalization import SemanticNormalizationSet
from qe_skill.semantic import SemanticCandidateSet


class ClarificationAnswer(d.Record):
    text: d.Text
    provenance: list[d.Ref] = Field(min_length=1)
    reviewer: d.Text
    answered_at: d.Timestamp


class ClarificationQuestion(d.Artifact):
    question: d.Text
    reason: d.Text
    category: d.Text
    blocking: bool
    sources: list[d.Ref] = Field(min_length=1)
    conflicting_sources: list[d.Ref] = Field(default_factory=list)
    affected: list[d.Ref] = Field(min_length=1)
    answer: ClarificationAnswer | None = None
    status: Literal["OPEN", "ANSWERED"] = "OPEN"
    output_language: d.OutputLanguage
    authority_changed: Literal[False] = False

    @model_validator(mode="after")
    def answer_matches_status(self) -> ClarificationQuestion:
        if (self.status == "ANSWERED") != (self.answer is not None):
            raise ValueError("clarification answer and status must change together")
        answer_refs = self.answer.provenance if self.answer else []
        for ref in self.sources + self.conflicting_sources + self.affected + answer_refs:
            if ref.project_id != self.project_id or ref.snapshot_id != self.snapshot_id:
                raise ValueError("cross-scope clarification reference")
        return self


class ClarificationSet(d.Artifact):
    normalization_set: d.Ref
    questions: list[ClarificationQuestion]
    project_locale: d.LanguageCode
    output_language: d.OutputLanguage
    external_writes: Literal[False] = False
    answers_fabricated: Literal[False] = False

    @model_validator(mode="after")
    def validate_scope(self) -> ClarificationSet:
        records: list[d.Artifact | d.Ref] = [self.normalization_set, *self.questions]
        if any(
            item.project_id != self.project_id or item.snapshot_id != self.snapshot_id
            for item in records
        ):
            raise ValueError("cross-scope clarification set")
        return self


_QUESTIONS = {
    "en": {
        "MODALITY_MISMATCH": "Which modality should govern this requirement?",
        "NEGATION_LOST": "Should the explicit negation in the cited source be preserved?",
        "CONSTRAINT_DIRECTION_MISMATCH": (
            "Which quantitative limit direction should govern this requirement?"
        ),
        "GROUNDING_MISSING": "Which cited source text supports this semantic interpretation?",
        "ALIAS_RELATION_MISSING": "Are the source term and canonical label approved aliases?",
        "NORMALIZATION_MISSING": "How should the cited source be interpreted semantically?",
        "NORMALIZATION_INVALID": "How should the invalid semantic interpretation be corrected?",
    },
    "pt-BR": {
        "MODALITY_MISMATCH": "Qual modalidade deve reger este requisito?",
        "NEGATION_LOST": "A negação explícita na fonte citada deve ser preservada?",
        "CONSTRAINT_DIRECTION_MISMATCH": (
            "Qual direção de limite quantitativo deve reger este requisito?"
        ),
        "GROUNDING_MISSING": (
            "Qual texto da fonte citada oferece suporte a esta interpretação semântica?"
        ),
        "ALIAS_RELATION_MISSING": ("O termo da fonte e o rótulo canônico são aliases aprovados?"),
        "NORMALIZATION_MISSING": "Como a fonte citada deve ser interpretada semanticamente?",
        "NORMALIZATION_INVALID": "Como a interpretação semântica inválida deve ser corrigida?",
    },
}


def questions_from_normalization(
    normalization: SemanticNormalizationSet,
    candidates: SemanticCandidateSet,
) -> ClarificationSet:
    """Create unanswered, provenance-bound questions; never synthesize an authoritative answer."""

    if (
        normalization.project_id != candidates.project_id
        or normalization.snapshot_id != candidates.snapshot_id
    ):
        raise ValueError("normalization and candidate scopes differ")
    candidate_index = {item.id: item for item in candidates.candidates}
    language = resolve_output_language(normalization.project_locale, normalization.output_language)
    catalog = _QUESTIONS["pt-BR" if language == "pt-BR" else "en"]
    questions: list[ClarificationQuestion] = []
    for issue in normalization.issues:
        candidate = candidate_index.get(issue.candidate.id)
        if candidate is None:
            continue
        sources = sorted(
            {evidence.source.id: evidence.source for evidence in candidate.evidence}.values(),
            key=lambda item: item.id,
        )
        payload = json.dumps(
            [normalization.id, issue.candidate.id, issue.code],
            separators=(",", ":"),
            ensure_ascii=False,
        )
        questions.append(
            ClarificationQuestion(
                id=f"clarification.{hashlib.sha256(payload.encode()).hexdigest()[:24]}",
                project_id=normalization.project_id,
                snapshot_id=normalization.snapshot_id,
                question=catalog[issue.code],
                reason=issue.message,
                category=issue.code,
                blocking=True,
                sources=sources,
                affected=[issue.candidate.model_copy(deep=True)],
                output_language=language,
            )
        )
    identity = json.dumps(
        [normalization.id, [item.id for item in questions], language],
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return ClarificationSet(
        id=f"clarifications.{hashlib.sha256(identity.encode()).hexdigest()[:24]}",
        project_id=normalization.project_id,
        snapshot_id=normalization.snapshot_id,
        normalization_set=d.Ref(
            id=normalization.id,
            project_id=normalization.project_id,
            snapshot_id=normalization.snapshot_id,
        ),
        questions=questions,
        project_locale=normalization.project_locale,
        output_language=language,
    )
