from typing import Dict
from day08_presentation.models import PresentationMode
from day09_observability.models import PipelineStats


# -------------------------
# Configuration (frozen defaults)
# -------------------------

MIN_EXPECTED_CHUNKS = 2
MIN_REQUIRED_CONTEXT_CHARS = 300


# -------------------------
# Confidence computation
# -------------------------
from day09_observability.models import DecisionTrace, PipelineLayer
from day08_presentation.models import PresentationMode


def compute_confidence(trace: DecisionTrace) -> float:
    """
    Deterministic confidence score derived from pipeline behavior.

    Range: [0.0, 1.0]
    """

    if not trace.allowed:
        return 0.0

    score = 1.0

    # Penalize warnings
    if trace.presentation_mode == PresentationMode.WARNING:
        score -= 0.2

    # Penalize failures earlier in pipeline
    for signal in trace.layer_signals:
        if not signal.passed:
            if signal.layer == PipelineLayer.DAY_06_ENTAILMENT:
                score -= 0.5
            elif signal.layer == PipelineLayer.DAY_07_CITATION_ALIGNMENT:
                score -= 0.3

    return max(score, 0.0)

# -------------------------
# Sub-score helpers
# -------------------------

def _compute_context_score(stats: PipelineStats) -> float:
    """
    Measures how complete and healthy the retrieved context was.
    """

    if stats is None:
        return 0.0

    chunk_score = min(
        stats.approved_chunks / MIN_EXPECTED_CHUNKS
        if stats.approved_chunks is not None else 0.0,
        1.0,
    )

    char_score = min(
        stats.total_context_chars / MIN_REQUIRED_CONTEXT_CHARS
        if stats.total_context_chars is not None else 0.0,
        1.0,
    )

    return round(min(chunk_score, char_score), 4)


def _compute_citation_score(
    *,
    aligned_citations: int,
    total_citations: int,
) -> float:
    """
    Measures citation correctness.
    """

    if total_citations == 0:
        return 0.0

    return round(aligned_citations / total_citations, 4)


def _presentation_multiplier(mode: PresentationMode) -> float:
    """
    Penalizes confidence based on exposure severity.
    """

    if mode == PresentationMode.FULL:
        return 1.0
    if mode == PresentationMode.WARNING:
        return 0.7
    if mode == PresentationMode.DEBUG:
        return 0.5

    return 0.0


# -------------------------
# Optional: confidence breakdown (human-readable)
# -------------------------

def confidence_breakdown(
    *,
    stats: PipelineStats,
    entailment_passed: bool,
    aligned_citations: int,
    total_citations: int,
    presentation_mode: PresentationMode,
) -> Dict[str, float]:
    """
    Returns explainable confidence components for reporting.
    """

    return {
        "context_score": _compute_context_score(stats),
        "entailment_score": 1.0 if entailment_passed else 0.0,
        "citation_score": _compute_citation_score(
            aligned_citations=aligned_citations,
            total_citations=total_citations,
        ),
        "presentation_score": _presentation_multiplier(presentation_mode),
    }