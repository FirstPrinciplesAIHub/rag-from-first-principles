import pytest

from day06_semantic_validation.claims import Claim

from day07_claim_citation_alignment.claim_citation_aligner import (
    align_claims_to_citations,
)
from day07_claim_citation_alignment.models import AlignmentStatus


def test_claim_missing_citation(sample_context_pack):
    claim = Claim(
        text="Refunds take 5–7 days.",
        source_sentence="Refunds take 5–7 days.",
        claim_id=1,
    )

    results = align_claims_to_citations(
        claims=[claim],
        sentence_text_to_citation_ids={},
        context_pack=sample_context_pack,
    )

    assert results[0].status == AlignmentStatus.MISSING_CITATION