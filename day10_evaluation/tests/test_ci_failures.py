from application.models import FinalAnswerResponse
from day08_presentation.models import PresentationMode
from day09_observability.models import PipelineStats
from day10_evaluation.drift import detect_regressions
from day10_evaluation.models import EvaluationResult

from day09_observability.models import DecisionTrace, PipelineLayer
from day08_presentation.models import PresentationMode


def test_ci_fails_on_any_regression():
    previous = [
        EvaluationResult(
            case_id="ci_case",
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
                query_text="ci_case",
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
            case_id="ci_case",
            response=FinalAnswerResponse(
                allowed=True,
                mode=PresentationMode.WARNING,  # regression
                answer_text="ok",
                citations=["doc"],
                refusal_reason=None,
                presentation_reason="partial",
            ),
            trace=DecisionTrace(
                query_id="q2",
                query_text="ci_case",
                layer_signals=[],
                allowed=True,
                presentation_mode=PresentationMode.WARNING,
                failure_layer=None,
                failure_code=None,
                refusal_reason=None,
                presentation_reason="partial",
            ),
            confidence=0.5,
        )
    ]

    regressions = detect_regressions(previous=previous, current=current)

    assert regressions, "CI must fail if any regression is detected"