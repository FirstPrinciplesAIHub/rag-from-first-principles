# day05_context_to_answer/pipeline.py

from day05_context_to_answer.answer_generator import generate_answer
from day05_context_to_answer.policies import GenerationPolicy


def answer_query(*, context_pack, llm, policy: GenerationPolicy = None):
    """
    End-to-end answer generation from a ContextPack.

    This function is the ONLY place where Day 4 meets Day 5.
    """

    if policy is None:
        policy = GenerationPolicy()

    return generate_answer(
        context_pack=context_pack,
        llm=llm,
        policy=policy,
    )