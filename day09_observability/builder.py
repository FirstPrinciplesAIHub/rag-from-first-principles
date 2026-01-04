# day09_observability/builder.py

import time
import uuid
from typing import Optional, List

from day09_observability.models import (
    DecisionTrace,
    LayerSignal,
    PipelineLayer,
    FailureCode,
    PipelineStats,
)
from day08_presentation.models import PresentationMode


def build_decision_trace(
    *,
    query_text: str,

    # ---- Day 4 ----
    context_valid: bool,
    context_failure_reason: Optional[str],

    # ---- Day 5 ----
    answer_refusal_reason: Optional[str],

    # ---- Day 6 ----
    entailment_passed: Optional[bool],
    entailment_failure_code: Optional[FailureCode],

    # ---- Day 7 ----
    citation_alignment_passed: Optional[bool],

    # ---- Day 8 ----
    presentation_mode: Optional[PresentationMode],
    presentation_reason: Optional[str],

    # ---- Observability ----
    stats: Optional[PipelineStats] = None,
    timestamps: Optional[dict] = None,
) -> DecisionTrace:
    """
    Build a DecisionTrace from already-computed pipeline results.

    This function:
    - makes NO decisions
    - performs NO validation
    - only records what already happened
    """

    now = time.time()
    query_id = str(uuid.uuid4())

    layer_signals: List[LayerSignal] = []

    failure_layer: Optional[PipelineLayer] = None
    failure_code: Optional[FailureCode] = None

    # ---------------- Day 4: Context ----------------
    if context_valid:
        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_04_CONTEXT,
                passed=True,
            )
        )
    else:
        failure_layer = PipelineLayer.DAY_04_CONTEXT
        failure_code = FailureCode.EMPTY_CONTEXT

        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_04_CONTEXT,
                passed=False,
                failure_code=failure_code,
                reason=context_failure_reason,
            )
        )

    # ---------------- Day 5: Generation ----------------
    if answer_refusal_reason is None:
        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_05_GENERATION,
                passed=True,
            )
        )
    else:
        failure_layer = PipelineLayer.DAY_05_GENERATION
        failure_code = FailureCode.MISSING_CITATION  # canonical Day-5 failure

        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_05_GENERATION,
                passed=False,
                failure_code=failure_code,
                reason=answer_refusal_reason,
            )
        )

        return DecisionTrace(
            query_id=query_id,
            query_text=query_text,
            layer_signals=layer_signals,
            allowed=False,
            presentation_mode=None,
            failure_layer=failure_layer,
            failure_code=failure_code,
            refusal_reason=answer_refusal_reason,
            presentation_reason=None,
            stats=stats or PipelineStats(),
            timestamps=timestamps or {"created_at": now},
        )

    # ---------------- Day 6: Entailment ----------------
    if entailment_passed is True:
        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_06_ENTAILMENT,
                passed=True,
            )
        )
    elif entailment_passed is False:
        failure_layer = PipelineLayer.DAY_06_ENTAILMENT
        failure_code = entailment_failure_code or FailureCode.NOT_ENTAILED

        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_06_ENTAILMENT,
                passed=False,
                failure_code=failure_code,
            )
        )

    # ---------------- Day 7: Citation Alignment ----------------
    if citation_alignment_passed is True:
        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_07_CITATION_ALIGNMENT,
                passed=True,
            )
        )
    elif citation_alignment_passed is False:
        failure_layer = PipelineLayer.DAY_07_CITATION_ALIGNMENT
        failure_code = FailureCode.MISALIGNED_CITATION

        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_07_CITATION_ALIGNMENT,
                passed=False,
                failure_code=failure_code,
            )
        )

    # ---------------- Day 8: Presentation ----------------
    allowed = presentation_mode in (
        PresentationMode.FULL,
        PresentationMode.WARNING,
        PresentationMode.DEBUG,
    )

    if presentation_mode is not None:
        layer_signals.append(
            LayerSignal(
                layer=PipelineLayer.DAY_08_PRESENTATION,
                passed=allowed,
                failure_code=(
                    FailureCode.SUPPRESSED_BY_POLICY
                    if presentation_mode == PresentationMode.SUPPRESSED
                    else None
                ),
                reason=presentation_reason,
            )
        )

    if presentation_mode == PresentationMode.SUPPRESSED:
        failure_layer = PipelineLayer.DAY_08_PRESENTATION
        failure_code = FailureCode.SUPPRESSED_BY_POLICY

    return DecisionTrace(
        query_id=query_id,
        query_text=query_text,
        layer_signals=layer_signals,
        allowed=allowed,
        presentation_mode=presentation_mode,
        failure_layer=failure_layer,
        failure_code=failure_code,
        refusal_reason=None,
        presentation_reason=presentation_reason,
        stats=stats or PipelineStats(),
        timestamps=timestamps or {"created_at": now},
    )