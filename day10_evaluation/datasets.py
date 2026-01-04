from typing import List
from day10_evaluation.models import GoldenCase
from day08_presentation.models import PresentationMode


# -------------------------------------------------------------------
# Core regression dataset
# -------------------------------------------------------------------

CORE_REGRESSION_DATASET: List[GoldenCase] = [
    GoldenCase(
        case_id="refuse_empty_context",
        query="What is the refund policy?",
        expected_allowed=False,
        expected_mode=PresentationMode.SUPPRESSED,
        expected_refusal_reason="empty_context",
        min_confidence=1.0,
    ),

    GoldenCase(
        case_id="suppress_unverified_claim",
        query="Tell me something risky",
        expected_allowed=False,
        expected_mode=PresentationMode.SUPPRESSED,
        expected_presentation_reason="unverified_claims",
        min_confidence=0.8,
    ),

    GoldenCase(
        case_id="allow_grounded_answer",
        query="How long does a refund take?",
        expected_allowed=True,
        expected_mode=PresentationMode.FULL,
        min_confidence=0.9,
    ),
]