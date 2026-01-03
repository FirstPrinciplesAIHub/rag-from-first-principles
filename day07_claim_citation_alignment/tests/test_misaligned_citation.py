from day06_semantic_validation.claims import Claim
from day07_claim_citation_alignment.claim_citation_aligner import (
    align_claims_to_citations,
)
from day07_claim_citation_alignment.models import AlignmentStatus


class DummyChunk:
    def __init__(self, chunk_id, text):
        self.chunk_id = chunk_id
        self.text = text


def test_misaligned_citation(sample_context_pack):
    claim = Claim(
        text="Refunds take 5–7 days.",
        source_sentence="Refunds take 5–7 days.",
        claim_id=1,
    )

    bad_chunk = DummyChunk(
        "chunk_1",
        "Shipping is free for all orders."
    )

    sample_context_pack.approved_chunks = [bad_chunk]
    sample_context_pack.dropped_chunks = []

    results = align_claims_to_citations(
        claims=[claim],
        sentence_text_to_citation_ids={
            "Refunds take 5–7 days.": ["chunk_1"]
        },
        context_pack=sample_context_pack,
    )

    assert results[0].status == AlignmentStatus.MISALIGNED