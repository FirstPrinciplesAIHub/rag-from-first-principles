from day05_context_to_answer.schemas import Answer
from day06_semantic_validation import claims
from day06_semantic_validation.entailment import check_entailment, EntailmentLabel
from day02_document_to_chunks.chunker import Chunk   # adjust import if needed


# -------------------------
# Fake LLM (strict)
# -------------------------
from day06_semantic_validation.tests.fake_llm import FakeLLM

# -------------------------
# Fixtures
# -------------------------

def build_context_chunks():
    return [
        Chunk(
            chunk_id="c1",
            section_title="Refund Policy",
            text="Refunds are processed within 5–7 business days.",
            doc_label="policy",
            confidence=0.95,
        )
    ]


# -------------------------
# Tests
# -------------------------

def test_entailment_returns_entailed_when_supported():
    llm = FakeLLM()
    context_chunks = build_context_chunks()

    result = check_entailment(
        claim_text="Refunds are processed within 5–7 business days.",
        context_chunks=context_chunks,
        llm=llm,
    )

    assert result.label == EntailmentLabel.ENTAILED
    assert result.supporting_chunk_ids == ["c1"]


def test_entailment_returns_not_entailed_when_unsupported():
    llm = FakeLLM()
    context_chunks = build_context_chunks()

    result = check_entailment(
        claim_text="Refunds are instant.",
        context_chunks=context_chunks,
        llm=llm,
    )

    assert result.label == EntailmentLabel.NOT_ENTAILED
    assert result.supporting_chunk_ids == []


def test_entailment_returns_not_entailed_when_no_context():
    llm = FakeLLM()

    result = check_entailment(
        claim_text="Refunds are processed within 5–7 business days.",
        context_chunks=[],
        llm=llm,
    )

    assert result.label == EntailmentLabel.NOT_ENTAILED


def test_entailment_returns_unknown_when_context_is_ambiguous():
    llm = FakeLLM()
    context_chunks = build_context_chunks()

    result = check_entailment(
        claim_text="Refunds depend on the payment method.",
        context_chunks=context_chunks,
        llm=llm,
    )

    assert result.label == EntailmentLabel.UNKNOWN