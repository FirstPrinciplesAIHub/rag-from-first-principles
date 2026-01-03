from day05_context_to_answer.pipeline import answer_query
from day05_context_to_answer.policies import GenerationPolicy


def test_answer_without_citation_is_rejected(fake_llm, sample_context_pack):
    fake_llm.fixed_response = (
        "Cancellations are allowed within 30 days of purchase."
    )

    answer = answer_query(
        context_pack=sample_context_pack,
        llm=fake_llm,
        policy=GenerationPolicy(),
    )

    assert "don't have enough information" in answer.text.lower()
    assert answer.refusal_reason == "missing_or_invalid_citations"


def test_answer_with_invalid_citation_is_rejected(fake_llm, sample_context_pack):
    fake_llm.fixed_response = (
        "Cancellations are allowed within 30 days. [random_blog]"
    )

    answer = answer_query(
        context_pack=sample_context_pack,
        llm=fake_llm,
        policy=GenerationPolicy(),
    )

    assert answer.refusal_reason == "missing_or_invalid_citations"