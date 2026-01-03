from day07_claim_citation_alignment.models import AlignmentStatus


def has_unverified_claims(claim_results) -> bool:
    return any(not r.verified for r in claim_results)


def has_misaligned_citations(citation_results) -> bool:
    return any(
        r.status != AlignmentStatus.ALIGNED
        for r in citation_results
    )