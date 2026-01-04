# day09_observability/tests/test_failure_classification.py

from day09_observability.recorder import TraceRecorder
from day09_observability.models import PipelineLayer, FailureCode, PresentationMode


from day09_observability.builder import build_decision_trace
from day09_observability.models import PipelineLayer, FailureCode
from day09_observability.recorder import TraceRecorder


def test_day5_refusal_is_attributed_correctly():
    trace = build_decision_trace(
        query_text="Some risky question",

        # Day 4
        context_valid=True,
        context_failure_reason=None,

        # Day 5
        answer_refusal_reason="missing_or_invalid_citations",

        # Downstream skipped
        entailment_passed=None,
        entailment_failure_code=None,
        citation_alignment_passed=None,

        presentation_mode=None,
        presentation_reason=None,
    )

    TraceRecorder.record(trace)

    assert trace.allowed is False
    assert trace.failure_layer == PipelineLayer.DAY_05_GENERATION
    assert trace.failure_code == FailureCode.MISSING_CITATION

    layers = [s.layer for s in trace.layer_signals]

    assert PipelineLayer.DAY_06_ENTAILMENT not in layers
    assert PipelineLayer.DAY_07_CITATION_ALIGNMENT not in layers
    assert PipelineLayer.DAY_08_PRESENTATION not in layers
    
    
from day09_observability.recorder import TraceRecorder
from day09_observability.models import PipelineLayer, FailureCode


from day09_observability.builder import build_decision_trace
from day09_observability.models import PipelineLayer, FailureCode
from day08_presentation.models import PresentationMode


def test_day6_entailment_failure():
    trace = build_decision_trace(
        query_text="What is the refund policy?",

        # Day 4
        context_valid=True,
        context_failure_reason=None,

        # Day 5
        answer_refusal_reason=None,

        # Day 6
        entailment_passed=False,
        entailment_failure_code=FailureCode.NOT_ENTAILED,

        # Day 7
        citation_alignment_passed=True,

        # Day 8
        presentation_mode=PresentationMode.FULL,
        presentation_reason=None,
    )

    assert trace.allowed is True   # presentation still allowed
    assert trace.failure_layer == PipelineLayer.DAY_06_ENTAILMENT
    assert trace.failure_code == FailureCode.NOT_ENTAILED