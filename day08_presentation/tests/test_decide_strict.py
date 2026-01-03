from day08_presentation.decide import decide_presentation
from day08_presentation.models import PresentationMode


def test_strict_policy_allows_clean_answer(
    policy_strict,
    verified_claims,
    aligned_citations,
):
    decision = decide_presentation(
        policy=policy_strict,
        claim_results=verified_claims,
        citation_results=aligned_citations,
    )

    assert decision.allowed is True
    assert decision.mode == PresentationMode.FULL
    assert decision.reason is None


def test_strict_policy_blocks_unverified_claim(
    policy_strict,
    unverified_claims,
    aligned_citations,
):
    decision = decide_presentation(
        policy=policy_strict,
        claim_results=unverified_claims,
        citation_results=aligned_citations,
    )

    assert decision.allowed is False
    assert decision.mode == PresentationMode.SUPPRESSED
    assert decision.reason is not None


def test_strict_policy_blocks_misaligned_citation(
    policy_strict,
    verified_claims,
    misaligned_citations,
):
    decision = decide_presentation(
        policy=policy_strict,
        claim_results=verified_claims,
        citation_results=misaligned_citations,
    )

    assert decision.allowed is False
    assert decision.mode == PresentationMode.SUPPRESSED