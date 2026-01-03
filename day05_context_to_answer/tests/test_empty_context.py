def test_refuses_on_empty_context(fake_llm, empty_context_pack):
    from day05_context_to_answer.answer_generator import generate_answer
    from day05_context_to_answer.policies import GenerationPolicy

    ans = generate_answer(
        context_pack=empty_context_pack,
        llm=fake_llm,
        policy=GenerationPolicy(),
    )

    assert "don't have enough information" in ans.text.lower()
    assert ans.refusal_reason == "empty_context"