from application.answer_service import answer_query_with_policy

def test_unverified_answer_is_suppressed_end_to_end(
    fake_llm,
    policy_strict,                    # presentation policy
    permissive_generation_policy,
    context_pack_with_content,
):
    response = answer_query_with_policy(
        context_pack=context_pack_with_content,
        llm=fake_llm,
        generation_policy=permissive_generation_policy,
        presentation_policy=policy_strict,
    )

    assert response.allowed is False
    assert response.answer_text is None
    assert response.citations is None

    # Not a Day-5 refusal
    assert response.refusal_reason == "missing_or_invalid_citations"

    # Day-8 suppression
    assert response.presentation_reason is  None