import pytest



from day06_semantic_validation.entailment import EntailmentLabel

# Import real classes from your project
from day04_retrieval_to_context.build_context import ContextPack
from day04_retrieval_to_context.build_context import ContextPolicy
from day02_document_to_chunks.chunker import Chunk   # adjust import if needed

from day06_semantic_validation.semantic_verifier import verify_answer


# -------------------------
# Fake LLM (strict + deterministic)
# -------------------------

from day06_semantic_validation.tests.fake_llm import FakeLLM

# -------------------------
# Fixtures
# -------------------------

@pytest.fixture
def approved_chunk():
    return Chunk(
        chunk_id="c1",
        section_title="Refund Policy",
        text="Refunds are processed within 5–7 business days.",
        doc_label="policy",
        confidence=0.95,
    )


@pytest.fixture
def dropped_chunk():
    return Chunk(
        chunk_id="c2",
        section_title="Old Policy",
        text="Refunds are instant.",
        doc_label="policy",
        confidence=0.40,
    )


@pytest.fixture
def context_pack(approved_chunk, dropped_chunk):
    return ContextPack(
        query="How do refunds work?",
        policy=ContextPolicy(),
        approved_chunks=[
            {"chunk": approved_chunk, "_reason": "relevant"},
        ],
        dropped_chunks=[
            {"chunk": dropped_chunk, "_drop_reason": "low confidence"},
        ],
        is_valid=True,
        invalid_reason=None,
        stats={},
    )


# -------------------------
# Tests
# -------------------------

def test_passes_when_all_claims_entailed(context_pack):
    llm = FakeLLM()

    answer = "Refunds are processed within 5–7 business days."

    report = verify_answer(
        answer_text=answer,
        context_pack=context_pack,
        llm=llm,
    )

    assert report.passed is True
    assert len(report.claim_results) == 1
    assert report.claim_results[0].label == EntailmentLabel.ENTAILED


def test_fails_when_claim_not_entailed(context_pack):
    llm = FakeLLM()

    answer = "Refunds are instant."

    report = verify_answer(
        answer_text=answer,
        context_pack=context_pack,
        llm=llm,
    )

    assert report.passed is False
    assert report.failure_reason is not None
    assert report.claim_results[0].label == EntailmentLabel.NOT_ENTAILED


def test_fails_when_no_context():
    llm = FakeLLM()

    empty_context = ContextPack(
        query="Refunds?",
        policy=ContextPolicy(),
        approved_chunks=[],
        dropped_chunks=[],
        is_valid=True,
        invalid_reason=None,
        stats={}
    )

    answer = "Refunds are processed within 5–7 business days."

    report = verify_answer(
        answer_text=answer,
        context_pack=empty_context,
        llm=llm,
    )

    assert report.passed is False
    assert report.claim_results[0].label == EntailmentLabel.NOT_ENTAILED


def test_passes_when_answer_has_no_factual_claims(context_pack):
    llm = FakeLLM()

    answer = "I think refunds are reasonable."

    report = verify_answer(
        answer_text=answer,
        context_pack=context_pack,
        llm=llm,
    )

    assert report.passed is True
    assert report.claim_results == []


def test_dropped_chunks_are_not_used(context_pack):
    llm = FakeLLM()

    # This claim exists ONLY in dropped chunk
    answer = "Refunds are instant."

    report = verify_answer(
        answer_text=answer,
        context_pack=context_pack,
        llm=llm,
    )

    assert report.passed is False