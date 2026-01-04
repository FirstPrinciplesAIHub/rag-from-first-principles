from application.models import FinalAnswerResponse
from day08_presentation.models import PresentationMode
from day09_observability.models import PipelineStats
from day10_evaluation.drift import detect_regressions
from day10_evaluation.models import EvaluationResult


def test_detects_allowed_regression():
    previous = [
        EvaluationResult(
            case_id="case_allowed",
            response=FinalAnswerResponse(
                allowed=True,
                mode=PresentationMode.FULL,
                answer_text="ok",
                citations=["doc"],
                refusal_reason=None,
                presentation_reason=None,
            ),
            trace=DecisionTrace(
                query_id="q1",
                query_text="case_allowed",
                layer_signals=[],
                allowed=True,
                presentation_mode=PresentationMode.FULL,
                failure_layer=None,
                failure_code=None,
                refusal_reason=None,
                presentation_reason=None,
            ),
            confidence=1.0,
        )
    ]

    current = [
        EvaluationResult(
            case_id="case_allowed",
            response=FinalAnswerResponse(
                allowed=False,  # REGRESSION
                mode=PresentationMode.SUPPRESSED,
                answer_text=None,
                citations=None,
                refusal_reason=None,
                presentation_reason="policy_block",
            ),
            trace=DecisionTrace(
                query_id="q2",
                query_text="case_allowed",
                layer_signals=[],
                allowed=False,
                presentation_mode=PresentationMode.SUPPRESSED,
                failure_layer=PipelineLayer.DAY_08_PRESENTATION,
                failure_code=None,
                refusal_reason=None,
                presentation_reason="policy_block",
            ),
            confidence=0.0,
        )
    ]

    regressions = detect_regressions(previous=previous, current=current)

    assert len(regressions) == 1
    assert regressions[0].metric == "allowed"
    
    
from day09_observability.models import DecisionTrace, PipelineLayer
from day08_presentation.models import PresentationMode


def test_detects_presentation_severity_regression():
    previous = [
        EvaluationResult(
            case_id="case_presentation",
            response=FinalAnswerResponse(
                allowed=True,
                mode=PresentationMode.FULL,
                answer_text="ok",
                citations=["doc"],
                refusal_reason=None,
                presentation_reason=None,
            ),
            trace=DecisionTrace(
                query_id="q1",
                query_text="case_presentation",
                layer_signals=[],
                allowed=True,
                presentation_mode=PresentationMode.FULL,
                failure_layer=None,
                failure_code=None,
                refusal_reason=None,
                presentation_reason=None,
            ),
            confidence=1.0,
        )
    ]

    current = [
        EvaluationResult(
            case_id="case_presentation",
            response=FinalAnswerResponse(
                allowed=True,
                mode=PresentationMode.WARNING,
                answer_text="ok",
                citations=["doc"],
                refusal_reason=None,
                presentation_reason="partial_context",
            ),
            trace=DecisionTrace(
                query_id="q2",
                query_text="case_presentation",
                layer_signals=[],
                allowed=True,
                presentation_mode=PresentationMode.WARNING,
                failure_layer=None,
                failure_code=None,
                refusal_reason=None,
                presentation_reason="partial_context",
            ),
            confidence=0.5,
        )
    ]

    regressions = detect_regressions(previous=previous, current=current)

    assert len(regressions) == 1

    r = regressions[0]
    assert r.metric == "presentation_severity"
    assert r.baseline_value == 0.0
    assert r.current_value == 0.5
    assert r.delta == 0.5