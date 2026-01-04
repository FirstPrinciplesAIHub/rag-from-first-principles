# day09_observability/tests/test_trace_capture.py

from day09_observability.recorder import TraceRecorder
from day09_observability.models import (
    PipelineLayer,
    PresentationMode,
    FailureCode,
)

from day09_observability.builder import build_decision_trace
from day09_observability.recorder import TraceRecorder
from day08_presentation.models import PresentationMode


def test_trace_records_successful_pipeline():
    TraceRecorder.clear()

    trace = build_decision_trace(
        query_text="What is the refund policy?",

        # Day 4
        context_valid=True,
        context_failure_reason=None,

        # Day 5
        answer_refusal_reason=None,

        # Day 6
        entailment_passed=True,
        entailment_failure_code=None,

        # Day 7
        citation_alignment_passed=True,

        # Day 8
        presentation_mode=PresentationMode.FULL,
        presentation_reason=None,
    )

    TraceRecorder.record(trace)

    traces = TraceRecorder.get_all()
    assert len(traces) == 1

    recorded = traces[0]
    assert recorded.allowed is True
    assert recorded.presentation_mode == PresentationMode.FULL
    assert recorded.failure_layer is None