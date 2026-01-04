from typing import List

from day10_evaluation.evaluators import detect_regressions
from day11_ci_locking.models import CIResult

    
# day11_ci_locking/runner.py

from day10_evaluation.models import EvaluationResult
from day11_ci_locking.models import GoldenBehavior


def extract_behavior(result: EvaluationResult) -> GoldenBehavior:
    """
    Project an EvaluationResult into the stable, externally visible
    behavior contract enforced by Day 11.
    """
    trace = result.trace

    return GoldenBehavior(
        case_id=result.case_id,
        allowed=result.response.allowed,
        presentation_mode=result.response.mode,
        failure_layer=trace.failure_layer if trace else None,
        failure_code=trace.failure_code if trace else None,
        confidence=result.confidence,
    )
    
    
def run_ci_check(
    *,
    baseline,
    current,
    report_generator,
) -> CIResult:
    """
    Compare current behavior against approved baseline.
    """

    regressions = detect_regressions(
        previous=baseline,
        current=current,
    )

    report = report_generator(regressions)

    return CIResult(
        passed=not regressions,
        regressions=regressions,
        report=report,
    )
