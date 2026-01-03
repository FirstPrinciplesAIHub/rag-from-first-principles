from day05_context_to_answer.pipeline import answer_query
from day05_context_to_answer.policies import GenerationPolicy


def test_end_to_end_context_to_answer(
    fake_llm,
    sample_context_pack,
):
    answer = answer_query(
        context_pack=sample_context_pack,
        llm=fake_llm,
        policy=GenerationPolicy(),
    )

    assert answer.text == fake_llm.fixed_response
    assert answer.citations == sample_context_pack.sources
    assert answer.refusal_reason is None