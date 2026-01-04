import pytest

from day05_context_to_answer.policies import GenerationPolicy
from day04_retrieval_to_context.build_context import ContextPack
from day04_retrieval_to_context.build_context import ContextPolicy


# -------------------------
# Generation policy
# -------------------------
@pytest.fixture
def permissive_generation_policy():
    return GenerationPolicy(
        refuse_if_no_context=False,
    )


# -------------------------
# Context pack with valid content
# -------------------------
@pytest.fixture
def context_pack_with_content():
    policy = ContextPolicy(
        max_chunks=5,
        min_chunks=1,
        min_chars=10,
    )

    return ContextPack(
        query="Some risky question",
        policy=policy,
        approved_chunks=[
            {
                "text": "Refunds are processed within 5–7 business days.",
                "metadata": {"source": "doc_1"},
                "_reason": "high_relevance",
            }
        ],
        dropped_chunks=[],
        is_valid=True,
        invalid_reason=None,
        stats={
            "approved_count": 1,
            "dropped_count": 0,
            "total_chars": 52,
        },
    )