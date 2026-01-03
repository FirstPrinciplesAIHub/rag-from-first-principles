def test_answer_is_grounded_in_context(fake_llm, sample_context_pack):
    """
    The model should answer using the provided context,
    and citations should come from the ContextPack.
    """
    from day05_context_to_answer.answer_generator import generate_answer
    from day05_context_to_answer.policies import GenerationPolicy

    policy = GenerationPolicy()

    answer = generate_answer(
        context_pack=sample_context_pack,
        llm=fake_llm,
        policy=policy,
    )

    # Answer text should be whatever fake_llm returns
    assert answer.text == fake_llm.fixed_response

    # Citations must be forwarded from ContextPack
    assert answer.citations == sample_context_pack.sources

    # No refusal when context exists
    assert answer.refusal_reason is None