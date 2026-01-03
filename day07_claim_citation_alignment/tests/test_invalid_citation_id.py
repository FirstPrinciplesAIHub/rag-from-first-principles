from day06_semantic_validation.claims import Claim
from day04_retrieval_to_context.build_context import ContextPack
from day07_claim_citation_alignment.claim_citation_aligner import (
    align_claims_to_citations,
)
from day07_claim_citation_alignment.models import AlignmentStatus


def test_invalid_citation_id(sample_context_pack):
    claim = Claim(
        text="Refunds take 5–7 days.",
        source_sentence="Refunds take 5–7 days.",
        claim_id=1,
    )

    sample_context_pack.approved_chunks = []
    sample_context_pack.dropped_chunks = []

    results = align_claims_to_citations(
        claims=[claim],
        sentence_text_to_citation_ids={
            "Refunds take 5–7 days.": ["chunk_999"]
        },
        context_pack=sample_context_pack,
    )

    assert results[0].status == AlignmentStatus.INVALID_CITATION