from day08_presentation.models import (
    PresentationDecision,
    PresentationMode,
    PresentationPolicy,
)
from day08_presentation.signals import (
    has_unverified_claims,
    has_misaligned_citations,
)


def decide_presentation(
    *,
    policy: PresentationPolicy,
    claim_results,
    citation_results,
) -> PresentationDecision:

    # Debug mode overrides everything
    if policy.debug_mode:
        return PresentationDecision(
            allowed=True,
            mode=PresentationMode.DEBUG,
            reason="Debug mode enabled",
        )

    unverified = has_unverified_claims(claim_results)
    misaligned = has_misaligned_citations(citation_results)

    # Hard block
    if unverified and not policy.allow_partial:
        return PresentationDecision(
            allowed=False,
            mode=PresentationMode.SUPPRESSED,
            reason="Unverified factual claims",
        )

    # Soft warning
    if unverified or misaligned:
        if policy.allow_warnings:
            return PresentationDecision(
                allowed=True,
                mode=PresentationMode.WARNING,
                reason="Some claims or citations could not be fully verified",
            )
        else:
            return PresentationDecision(
                allowed=False,
                mode=PresentationMode.SUPPRESSED,
                reason="Policy disallows warnings",
            )

    # Clean pass
    return PresentationDecision(
        allowed=True,
        mode=PresentationMode.FULL,
        reason=None,
    )