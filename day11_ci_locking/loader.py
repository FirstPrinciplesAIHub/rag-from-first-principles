# day11_ci_locking/loader.py

from typing import List
from day10_evaluation.models import EvaluationResult


def load_golden_results(module) -> List[EvaluationResult]:
    """
    Load golden results from a Python snapshot module.
    """
    return list(module.GOLDEN_RESULTS)