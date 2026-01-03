import pytest

from build_context import (
    ContextPolicy,
    select_chunks,
    order_chunks,
    build_context_pack,
)

@pytest.fixture
def sample_retrieval_chunks():
    """
    Provide a stable, representative retrieval result.

    Purpose:
    - Acts as a controlled input for context assembly tests
    - Covers boilerplate, headers, and explanatory content

    Why this matters:
    - RAG tests must be deterministic
    - Retrieval noise is simulated, not random
    """
    return [
        {
            "text": "DOCUMENT_START\nCompany Policy",
            "distance": 0.05,
            "metadata": {}
        },
        {
            "text": "Cancellation Policy",
            "distance": 0.10,
            "metadata": {"chunk_index": 1}
        },
        {
            "text": "You may cancel within 30 days for a full refund.",
            "distance": 0.12,
            "metadata": {"chunk_index": 2}
        },
        {
            "text": "Refunds are processed within 5–7 business days.",
            "distance": 0.18,
            "metadata": {"chunk_index": 3}
        },
        {
            "text": "COPYRIGHT 2022 ACME CORP",
            "distance": 0.01,
            "metadata": {}
        },
    ]


def test_context_not_empty(sample_retrieval_chunks):
    """
    Ensure that valid explanatory content is not accidentally filtered out.

    Why this matters:
    - An empty context leads to guaranteed hallucination
    - This test guards against overly aggressive policies
    """
    policy = ContextPolicy()

    approved, dropped = select_chunks(sample_retrieval_chunks, policy)
    ordered = order_chunks(approved)
    pack = build_context_pack(
        query="How does cancellation work?",
        policy=policy,
        approved_chunks=ordered,
        dropped_chunks=dropped,
    )

    assert pack.stats["approved_count"] > 0


def test_boilerplate_is_dropped(sample_retrieval_chunks):
    """
    Verify that boilerplate content never reaches context.

    Why this matters:
    - Boilerplate scoring highly is a known embedding failure mode
    - This must be invariant across policy changes
    """
    policy = ContextPolicy()

    approved, dropped = select_chunks(sample_retrieval_chunks, policy)

    dropped_texts = [d["text"] for d in dropped]

    assert any("DOCUMENT_START" in t for t in dropped_texts)
    assert any("COPYRIGHT" in t for t in dropped_texts)


def test_headers_are_dropped(sample_retrieval_chunks):
    """
    Ensure that structural headers are excluded from context.

    Why this matters:
    - Headers often outrank explanations in embeddings
    - Passing them to the LLM degrades reasoning
    """
    policy = ContextPolicy()

    approved, dropped = select_chunks(sample_retrieval_chunks, policy)

    approved_texts = [c["text"] for c in approved]

    assert "Cancellation Policy" not in approved_texts

def test_dropped_chunks_have_reasons(sample_retrieval_chunks):
    """
    Ensure that every dropped chunk includes a drop reason.

    Why this matters:
    - Silent exclusion is unacceptable in explainable RAG
    - Every decision must be traceable
    """
    policy = ContextPolicy()

    _, dropped = select_chunks(sample_retrieval_chunks, policy)

    for d in dropped:
        assert "_drop_reason" in d
        assert isinstance(d["_drop_reason"], str)
        assert d["_drop_reason"]

def test_context_stats_consistency(sample_retrieval_chunks):
    """
    Verify internal consistency of ContextPack statistics.

    Why this matters:
    - Stats are used for monitoring and alerts
    - Inconsistent stats indicate logic bugs
    """
    policy = ContextPolicy()

    approved, dropped = select_chunks(sample_retrieval_chunks, policy)
    ordered = order_chunks(approved)

    pack = build_context_pack(
        query="How does cancellation work?",
        policy=policy,
        approved_chunks=ordered,
        dropped_chunks=dropped,
    )

    stats = pack.stats

    assert stats["approved_count"] == len(pack.approved_chunks)
    assert stats["dropped_count"] == len(pack.dropped_chunks)
    assert stats["used_chars"] >= 0
    assert stats["used_chars"] <= stats["max_chars"]

def test_policy_max_chunks_limit(sample_retrieval_chunks):
    """
    Verify that policy changes have predictable effects.

    Why this matters:
    - Policy must control behavior, not hidden logic
    """
    policy = ContextPolicy(max_chunks=1)

    approved, _ = select_chunks(sample_retrieval_chunks, policy)

    assert len(approved) == 1

def test_empty_context_is_invalid(sample_retrieval_chunks):
    """
    Ensure weak or empty context is explicitly rejected.
    """

    policy = ContextPolicy(
        max_chars=10,   # force failure
        min_chars=50,
    )

    approved, dropped = select_chunks(sample_retrieval_chunks, policy)
    ordered = order_chunks(approved)

    pack = build_context_pack(
        query="test",
        policy=policy,
        approved_chunks=ordered,
        dropped_chunks=dropped,
    )

    assert pack.is_valid is False
    assert pack.invalid_reason is not None