from day07_claim_citation_alignment.models import AlignmentStatus


from day06_semantic_validation.entailment import EntailmentLabel


def has_unverified_claims(claim_results) -> bool:
    return any(
        r.label != EntailmentLabel.ENTAILED
        for r in claim_results
    )

def has_misaligned_citations(citation_results) -> bool:
    if not citation_results:
        return False
    return any(
        r.status != AlignmentStatus.ALIGNED
        for r in citation_results
    )