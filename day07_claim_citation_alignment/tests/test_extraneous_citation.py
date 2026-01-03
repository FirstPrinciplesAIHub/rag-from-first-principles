from day06_semantic_validation.claims import Claim 
from day07_claim_citation_alignment.claim_citation_aligner import (
    align_claims_to_citations,
)
from day07_claim_citation_alignment.models import AlignmentStatus


def test_extraneous_citation(sample_context_pack, make_chunk):
    claim = Claim(
        text="Refunds take 5–7 days.",
        source_sentence="Refunds take 5–7 days.",
        claim_id=1,
    )

    supporting = make_chunk(
        "chunk_1",
        "Refunds take 5–7 days after cancellation."
    )
    extra = make_chunk(
        "chunk_2",
        "Shipping is free."
    )

    sample_context_pack.approved_chunks = [supporting, extra]

    results = align_claims_to_citations(
        claims=[claim],
        sentence_text_to_citation_ids={
            "Refunds take 5–7 days.": ["chunk_1", "chunk_2"]
        },
        context_pack=sample_context_pack,
    )

    assert results[0].status == AlignmentStatus.EXTRANEOUS_CITATION