def test_model_refuses_when_answer_not_in_context(fake_llm, thin_context_pack):
    """
    Even if context exists, the model must refuse
    if the answer is not present in the context.
    """
    from day05_context_to_answer.answer_generator import generate_answer
    from day05_context_to_answer.policies import GenerationPolicy

    # Fake LLM is instructed to refuse explicitly
    fake_llm.fixed_response = "I don't have enough information to answer."

    answer = generate_answer(
        context_pack=thin_context_pack,
        llm=fake_llm,
        policy=GenerationPolicy(),
    )

    assert "don't have enough information" in answer.text.lower()
    assert answer.refusal_reason is None  # model refusal, not system refusal