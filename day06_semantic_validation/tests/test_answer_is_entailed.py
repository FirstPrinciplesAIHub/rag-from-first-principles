from day06_semantic_validation.semantic_verifier import verify_answer
from day06_semantic_validation.entailment import EntailmentLabel

from day04_retrieval_to_context.build_context import ContextPack
from day04_retrieval_to_context.build_context import ContextPolicy
from day02_document_to_chunks.chunker import Chunk
from day06_semantic_validation.tests.fake_llm import FakeLLM



def build_context_pack():
    approved = Chunk(
        chunk_id="c1",
        section_title="Refund Policy",
        text="Refunds are processed within 5–7 business days.",
        doc_label="policy",
        confidence=0.9,
    )

    return ContextPack(
        query="Refunds?",
        policy=ContextPolicy(),
        approved_chunks=[{"chunk": approved}],
        dropped_chunks=[],
        is_valid=True,
        invalid_reason=None,
        stats={},
    )


def test_answer_passes_when_all_claims_entailed():
    context = build_context_pack()
    llm = FakeLLM()

    answer = "Refunds are processed within 5–7 business days."

    report = verify_answer(
        answer_text=answer,
        context_pack=context,
        llm=llm,
    )

    assert report.passed is True


def test_answer_fails_if_any_claim_not_entailed():
    context = build_context_pack()
    llm = FakeLLM()

    answer = (
        "Refunds are processed within 5–7 business days. "
        "Refunds are instant."
    )

    report = verify_answer(
        answer_text=answer,
        context_pack=context,
        llm=llm,
    )

    assert report.passed is False
    assert report.failure_reason is not None