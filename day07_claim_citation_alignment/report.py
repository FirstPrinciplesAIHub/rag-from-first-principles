from dataclasses import dataclass
from typing import List, Optional

from day07_claim_citation_alignment.models import (
    AlignmentStatus,
    ClaimCitationResult,
)


@dataclass
class ClaimCitationReport:
    """
    Aggregated report for claim ↔ citation alignment.

    This is the object consumed by:
    - CI pipelines
    - API responses
    - UI layers
    """

    passed: bool
    results: List[ClaimCitationResult]
    failure_reason: Optional[str] = None


def build_claim_citation_report(
    results: List[ClaimCitationResult],
) -> ClaimCitationReport:
    """
    Build an aggregate report from individual claim-citation results.

    Rules:
    - Any MISSING_CITATION → FAIL
    - Any INVALID_CITATION → FAIL
    - Any MISALIGNED → FAIL
    - EXTRANEOUS_CITATION → PASS (but visible)
    - ALIGNED → PASS
    """

    if not results:
        # No claims → nothing to align → pass
        return ClaimCitationReport(
            passed=True,
            results=[],
            failure_reason=None,
        )

    for result in results:
        if result.status in {
            AlignmentStatus.MISSING_CITATION,
            AlignmentStatus.INVALID_CITATION,
            AlignmentStatus.MISALIGNED,
        }:
            return ClaimCitationReport(
                passed=False,
                results=results,
                failure_reason=(
                    f"Claim at sentence {result.sentence_index} failed: "
                    f"{result.status.value}"
                ),
            )

    return ClaimCitationReport(
        passed=True,
        results=results,
        failure_reason=None,
    )