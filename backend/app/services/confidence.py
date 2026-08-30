"""Rule-based diagnosis confidence scoring.

This is deliberately simple and transparent — NOT a calibrated probability.
Signals considered:

1. Whether an error type was detected.
2. Whether a language was detected (and with what certainty).
3. Retrieval relevance (best similarity score).
4. Keyword overlap between the analysis keywords and retrieved content.
"""
from dataclasses import dataclass
from typing import List, Optional

from app.rag.retriever import RetrievedChunk

from .error_analyzer import AnalysisResult


@dataclass
class ConfidenceResult:
    level: str  # High | Medium | Low
    score: float  # 0..1
    reason: str


def _max_similarity(chunks: List[RetrievedChunk]) -> float:
    if not chunks:
        return 0.0
    return max(c.similarity for c in chunks)


def _keyword_overlap(analysis: AnalysisResult, chunks: List[RetrievedChunk]) -> float:
    if not analysis.keywords or not chunks:
        return 0.0
    haystack = " ".join(c.content.lower() for c in chunks[:6])
    hit = sum(1 for kw in analysis.keywords[:8] if kw.lower() in haystack)
    return hit / min(len(analysis.keywords[:8]), 8)


def _label(score: float) -> str:
    if score >= 0.7:
        return "High"
    if score >= 0.4:
        return "Medium"
    return "Low"


def compute_confidence(
    analysis: AnalysisResult,
    chunks: List[RetrievedChunk],
) -> ConfidenceResult:
    """Return a ConfidenceResult with a human-readable reason string."""
    reasons: list = []

    # 1) Error type detected?
    if analysis.detected_error:
        reasons.append("error type detected")
        type_signal = 1.0
    else:
        reasons.append("error type could not be identified")
        type_signal = 0.0

    # 2) Language detected?
    lang_signal = 0.0
    if analysis.language and analysis.language.lower() not in ("unknown", ""):
        if analysis.language_confidence == "High":
            lang_signal = 1.0
        elif analysis.language_confidence == "Medium":
            lang_signal = 0.7
        else:
            lang_signal = 0.4
        reasons.append(f"language detected ({analysis.language})")
    else:
        reasons.append("language could not be detected")

    # 3) Retrieval relevance.
    best = _max_similarity(chunks)
    retrieval_signal = min(1.0, max(0.0, best))
    if best >= 0.45:
        reasons.append("strongly relevant knowledge found")
    elif best >= 0.2:
        reasons.append("partially relevant knowledge found")
    else:
        reasons.append("little relevant knowledge retrieved")

    # 4) Keyword overlap into retrieved content.
    overlap = _keyword_overlap(analysis, chunks)
    reasons.append("keywords match retrieved material" if overlap >= 0.4 else "keyword match is weak")

    score = 0.35 * type_signal + 0.25 * lang_signal + 0.25 * retrieval_signal + 0.15 * overlap

    reason = "; ".join(reasons)
    if score < 0.4:
        reason += ". More context (full stack trace or surrounding code) may be required."

    return ConfidenceResult(level=_label(score), score=round(score, 3), reason=reason)