# day09_observability/models.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------
# Enums
# ---------------------------------------------------------

class PipelineLayer(Enum):
    DAY_04_CONTEXT = "day_04_context"
    DAY_05_GENERATION = "day_05_generation"
    DAY_06_ENTAILMENT = "day_06_entailment"
    DAY_07_CITATION_ALIGNMENT = "day_07_citation_alignment"
    DAY_08_PRESENTATION = "day_08_presentation"


class FailureCode(Enum):
    # Context layer
    EMPTY_CONTEXT = "empty_context"
    INSUFFICIENT_CONTEXT = "insufficient_context"

    # Generation layer
    MISSING_CITATION = "missing_citation"
    INVALID_CITATION = "invalid_citation"

    # Semantic validation
    NOT_ENTAILED = "not_entailed"
    UNKNOWN_ENTAILMENT = "unknown_entailment"

    # Citation alignment
    MISALIGNED_CITATION = "misaligned_citation"
    EXTRANEOUS_CITATION = "extraneous_citation"

    # Presentation
    SUPPRESSED_BY_POLICY = "suppressed_by_policy"


class PresentationMode(Enum):
    NORMAL = "normal"
    WARNING = "warning"
    SUPPRESSED = "suppressed"


# ---------------------------------------------------------
# Per-layer signal (atomic, explainable)
# ---------------------------------------------------------

@dataclass(frozen=True)
class LayerSignal:
    """
    Records the outcome of a single pipeline layer.

    This object MUST NOT encode behavior.
    It only records what happened.
    """

    layer: PipelineLayer

    passed: bool

    failure_code: Optional[FailureCode] = None
    reason: Optional[str] = None


# ---------------------------------------------------------
# Aggregated numeric stats (optional but powerful)
# ---------------------------------------------------------

@dataclass(frozen=True)
class PipelineStats:
    """
    Numeric metrics collected during the pipeline run.

    These are safe to log, aggregate, and monitor.
    """

    # -------- Day 4 --------
    retrieved_chunks: Optional[int] = None
    approved_chunks: Optional[int] = None
    dropped_chunks: Optional[int] = None
    total_context_chars: Optional[int] = None

    # -------- Day 6 --------
    claim_count: Optional[int] = None
    entailed_claims: Optional[int] = None

    # -------- Day 7 --------
    aligned_citations: Optional[int] = None
    misaligned_citations: Optional[int] = None

    # -------- Day 12 (NEW) --------
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None

# ---------------------------------------------------------
# Final trace (one per user query)
# ---------------------------------------------------------

@dataclass(frozen=True)
class DecisionTrace:
    query_id: str
    query_text: str

    layer_signals: List[LayerSignal]

    allowed: bool
    presentation_mode: Optional[PresentationMode]

    failure_layer: Optional[PipelineLayer]
    failure_code: Optional[FailureCode]

    refusal_reason: Optional[str]
    presentation_reason: Optional[str]

    stats: PipelineStats = field(default_factory=PipelineStats)
    timestamps: Dict[str, float] = field(default_factory=dict)