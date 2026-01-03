from day05_context_to_answer.pipeline import answer_query
from day05_context_to_answer.policies import GenerationPolicy


def test_hallucinated_answer_without_citation_is_rejected(
    fake_llm,
    sample_context_pack,
):
    # Model gives a confident answer, but no citation
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

def test_hallucinated_fake_source_is_rejected(
    fake_llm,
    sample_context_pack,
):
    # Model cites a source that was never provided
    fake_llm.fixed_response = (
        "Cancellations are allowed within 30 days. "
        "[wikipedia.org/cancellation-policy]"
    )

    answer = answer_query(
        context_pack=sample_context_pack,
        llm=fake_llm,
        policy=GenerationPolicy(),
    )

    assert answer.refusal_reason == "missing_or_invalid_citations"


def test_confident_but_fabricated_answer_is_rejected(
    fake_llm,
    sample_context_pack,
):
    fake_llm.fixed_response = (
        "Customers receive a full refund after 90 days. "
        "[policy_a.pdf#section-3]"
    )

    answer = answer_query(
        context_pack=sample_context_pack,
        llm=fake_llm,
        policy=GenerationPolicy(),
    )

    # Citation is syntactically valid, but content is wrong
    # NOTE: This is where *future* semantic validation can be added
    # For now, system correctly allows it (important limitation)
    assert answer.refusal_reason is None