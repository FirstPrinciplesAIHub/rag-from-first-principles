from typing import List

from application.answer_service import answer_query_with_policy
from day09_observability.recorder import TraceRecorder
from day10_evaluation.models import (
    GoldenCase,
    EvaluationResult,
)
from day10_evaluation.metrics import compute_confidence


def run_case(
    *,
    case: GoldenCase,
    context_pack,
    llm,
    generation_policy,
    presentation_policy,
) -> EvaluationResult:
    """
    Run a single GoldenCase through the full pipeline.

    - Executes the real pipeline
    - Captures FinalAnswerResponse (Day 8)
    - Captures DecisionTrace (Day 9)
    - Computes confidence (Day 10)
    """

    # Ensure isolation
    TraceRecorder.clear()

    response = answer_query_with_policy(
        context_pack=context_pack,
        llm=llm,
        generation_policy=generation_policy,
        presentation_policy=presentation_policy,
    )

    traces = TraceRecorder.get_all()

    # 🚨 HARD GUARANTEE — trace must exist
    if not traces:
        raise RuntimeError(
            f"No DecisionTrace recorded for case '{case.case_id}'. "
            "This indicates a broken Day-09 observability contract."
        )

    trace = traces[-1]

    confidence = compute_confidence(trace)

    return EvaluationResult(
        case_id=case.case_id,
        response=response,
        trace=trace,
        confidence=confidence,
    )
    
def run_dataset(
    *,
    cases: List[GoldenCase],
    context_pack_factory,
    llm,
    generation_policy,
    presentation_policy,
) -> List[EvaluationResult]:
    """
    Execute a dataset of GoldenCases.
    """

    results: List[EvaluationResult] = []

    for case in cases:
        context_pack = context_pack_factory(case.query)

        result = run_case(
            case=case,
            context_pack=context_pack,
            llm=llm,
            generation_policy=generation_policy,
            presentation_policy=presentation_policy,
        )

        results.append(result)

    return results