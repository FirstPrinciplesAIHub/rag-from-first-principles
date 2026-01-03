from day08_presentation.decide import decide_presentation
from day08_presentation.models import PresentationMode


def test_debug_mode_overrides_all_failures(
    policy_debug,
    unverified_claims,
    misaligned_citations,
):
    decision = decide_presentation(
        policy=policy_debug,
        claim_results=unverified_claims,
        citation_results=misaligned_citations,
    )

    assert decision.allowed is True
    assert decision.mode == PresentationMode.DEBUG
    assert decision.reason is not None