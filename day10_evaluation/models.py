from dataclasses import dataclass
from typing import Optional
from day08_presentation.models import PresentationMode


@dataclass(frozen=True)
class GoldenCase:
    """
    A single evaluation contract for the RAG pipeline.

    This does NOT assert answer text.
    It asserts behavioral outcomes and safety guarantees.
    """

    case_id: str
    query: str

    # Expected high-level behavior
    expected_allowed: bool
    expected_mode: PresentationMode

    # Expected reasons (if applicable)
    expected_refusal_reason: Optional[str] = None
    expected_presentation_reason: Optional[str] = None

    # Confidence expectations
    min_confidence: float = 0.0
    

from dataclasses import dataclass
from application.models import FinalAnswerResponse
from day09_observability.models import PipelineStats

from enum import Enum
from typing import Optional


class EvaluationStatus(Enum):
    PASS = "pass"
    FAIL = "fail"


@dataclass(frozen=True)
class EvaluatedOutcome:
    """
    Judgment applied to an EvaluationResult.
    """

    case_id: str
    status: EvaluationStatus
    confidence: float
    failure_reason: Optional[str] = None
    
    
from dataclasses import dataclass
from typing import Optional

from application.models import FinalAnswerResponse
from day09_observability.models import PipelineStats


from dataclasses import dataclass
from typing import Optional

from application.models import FinalAnswerResponse
from day09_observability.models import DecisionTrace


@dataclass(frozen=True)
class EvaluationResult:
    case_id: str
    response: FinalAnswerResponse
    trace: Optional[DecisionTrace]
    confidence: float

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class CaseEvaluation:
    """
    Result of evaluating one GoldenCase.
    """

    case_id: str
    passed: bool

    confidence: float
    failure_reasons: List[str]
    

from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceBreakdown:
    """
    Explainable confidence components.
    """

    entailment_score: float
    citation_alignment_score: float
    context_strength_score: float
    refusal_penalty: float
    
from dataclasses import dataclass


@dataclass(frozen=True)
class Regression:
    """
    Represents a detected behavioral regression.
    """

    case_id: str
    metric: str

    baseline_value: float
    current_value: float

    delta: float
    
from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class EvaluationSummary:
    """
    Aggregate evaluation outcome for a dataset.
    """

    total_cases: int
    passed_cases: int
    failed_cases: int

    average_confidence: float

    regressions: List[Regression]

from dataclasses import dataclass
from typing import List
from day10_evaluation.models import Regression


@dataclass(frozen=True)
class RegressionReport:
    """
    Human-readable regression report.
    """

    summary: str
    case_sections: List[str]
    ci_verdict: str