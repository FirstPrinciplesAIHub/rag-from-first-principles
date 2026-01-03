from day08_presentation.decide import decide_presentation
from day08_presentation.models import PresentationMode


def test_warning_policy_allows_unverified_claim_with_warning(
    policy_permissive,
    unverified_claims,
    aligned_citations,
):
    decision = decide_presentation(
        policy=policy_permissive,
        claim_results=unverified_claims,
        citation_results=aligned_citations,
    )

    assert decision.allowed is True
    assert decision.mode == PresentationMode.WARNING
    assert decision.reason is not None


def test_warning_policy_allows_misaligned_citation(
    policy_permissive,
    verified_claims,
    misaligned_citations,
):
    decision = decide_presentation(
        policy=policy_permissive,
        claim_results=verified_claims,
        citation_results=misaligned_citations,
    )

    assert decision.allowed is True
    assert decision.mode == PresentationMode.WARNING