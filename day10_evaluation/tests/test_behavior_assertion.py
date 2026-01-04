from application.models import FinalAnswerResponse
from day09_observability.models import DecisionTrace
from day08_presentation.models import PresentationMode
from day10_evaluation.drift import detect_regressions
from day10_evaluation.models import EvaluationResult


def test_no_regression_when_behavior_unchanged():
    previous = [
        EvaluationResult(
            case_id="stable_case",
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
                query_text="stable_case",
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
            case_id="stable_case",
            response=FinalAnswerResponse(
                allowed=True,
                mode=PresentationMode.FULL,
                answer_text="ok",
                citations=["doc"],
                refusal_reason=None,
                presentation_reason=None,
            ),
            trace=DecisionTrace(
                query_id="q2",
                query_text="stable_case",
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

    regressions = detect_regressions(previous=previous, current=current)

    assert regressions == []