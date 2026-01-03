import pytest
from day05_context_to_answer.policies import GenerationPolicy
from day08_presentation.models import PresentationPolicy
from day07_claim_citation_alignment.models import (
    AlignmentStatus,
    ClaimCitationResult,
)


# ---------- Policies ----------

@pytest.fixture
def policy_strict():
    return PresentationPolicy(
        allow_partial=False,
        allow_warnings=False,
        debug_mode=False,
    )


@pytest.fixture
def policy_permissive():
    return PresentationPolicy(
        allow_partial=True,
        allow_warnings=True,
        debug_mode=False,
    )


@pytest.fixture
def policy_debug():
    return PresentationPolicy(
        allow_partial=True,
        allow_warnings=True,
        debug_mode=True,
    )


# ---------- Claim results (Day 6 output) ----------

class FakeClaimResult:
    def __init__(self, verified: bool):
        self.verified = verified


@pytest.fixture
def verified_claims():
    return [
        FakeClaimResult(verified=True),
        FakeClaimResult(verified=True),
    ]


@pytest.fixture
def unverified_claims():
    return [
        FakeClaimResult(verified=True),
        FakeClaimResult(verified=False),
    ]


# ---------- Citation results (Day 7 output) ----------
@pytest.fixture
def aligned_citations():
    return [
        ClaimCitationResult(
            claim_text="Refunds are processed within 5–7 business days.",
            sentence_index=0,
            cited_ids=["doc_1"],
            status=AlignmentStatus.ALIGNED,
        )
    ]


@pytest.fixture
def misaligned_citations():
    return [
        ClaimCitationResult(
            claim_text="Refunds are processed within 5–7 business days.",
            sentence_index=0,
            cited_ids=[],
            status=AlignmentStatus.MISSING_CITATION,
        )
    ]
    
import pytest


class FakeLLM:
    def generate(self, *, prompt, max_tokens, temperature):
        # Return an answer that LOOKS confident
        # but will fail semantic verification (Day 6)
        return "Refunds are processed instantly."
    

@pytest.fixture
def fake_llm():
    return FakeLLM()

import pytest

@pytest.fixture
def permissive_generation_policy():
    """
    Generation policy that allows answer generation
    (i.e., does NOT refuse due to empty context).
    """
    return GenerationPolicy(
        refuse_if_no_context=False,
    )
    
import pytest
from day04_retrieval_to_context.build_context import ContextPack, ContextPolicy



import pytest
from day04_retrieval_to_context.build_context import ContextPack


@pytest.fixture
def context_pack_with_content():
    """
    Valid ContextPack with sufficient evidence so
    Day 5–8 can execute end-to-end.
    """
    policy = ContextPolicy(
        max_chunks=5,
        max_chars=3000,
        min_chunks=1,
        min_chars=100,
        header_max_chars=40,
        uppercase_header_max_chars=80,
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