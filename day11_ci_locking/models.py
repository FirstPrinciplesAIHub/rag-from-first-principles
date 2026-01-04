from dataclasses import dataclass
from typing import List

from day10_evaluation.models import EvaluationResult
from day10_evaluation.models import Regression


@dataclass(frozen=True)
class GoldenSnapshot:
    """
    A frozen, approved snapshot of pipeline behavior.
    """

    version: str
    results: List[EvaluationResult]


@dataclass(frozen=True)
class CIResult:
    """
    Outcome of CI regression check.
    """

    passed: bool
    regressions: List[Regression]
    report: str
    
    
from dataclasses import dataclass
from typing import Optional

from day08_presentation.models import PresentationMode
from day09_observability.models import PipelineLayer, FailureCode


@dataclass(frozen=True)
class GoldenBehavior:
    """
    Approved, externally visible behavior for one query.
    """

    case_id: str

    # Final response contract
    allowed: bool
    presentation_mode: PresentationMode

    # Failure semantics (if any)
    failure_layer: Optional[PipelineLayer]
    failure_code: Optional[FailureCode]

    # Quantitative stability
    confidence: float