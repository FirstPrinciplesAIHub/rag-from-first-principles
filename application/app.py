import logging
from day04_retrieval_to_context.build_context import ContextPolicy
from application.context_builder import build_context_for_query
from application.answer_service import answer_query_with_policy
from infrastructure.llm.factory import build_llm
from day05_context_to_answer.policies import GenerationPolicy
from day08_presentation.models import PresentationPolicy

from infrastructure.llm.factory import build_llm

logger = logging.getLogger(__name__)

llm = build_llm()
logger.info(f"[LLM] Using backend: {llm.__class__.__name__}")

def main():
    query = "How long does a refund take?"

   
    # -------------------------
    # Policies
    # -------------------------
    context_policy = ContextPolicy(
        max_chunks=5,
        max_chars=3000,
        min_chunks=1,
        min_chars=50,
    )

    generation_policy = GenerationPolicy(
        refuse_if_no_context=True,
    )

    presentation_policy = PresentationPolicy(
        allow_partial=False,
        allow_warnings=True,
        debug_mode=False,
    )

    # -------------------------
    # LLM (Fake or Real)
    # -------------------------
    llm = build_llm()  # FakeLLM by default, OpenAI later

    # -------------------------
    # Build context (Day 3 → Day 4)
    # -------------------------
    context_pack = build_context_for_query(
        query=query,
        policy=context_policy,
    )

    # -------------------------
    # Full pipeline (Day 5 → Day 9)
    # -------------------------
    response = answer_query_with_policy(
        context_pack=context_pack,
        llm=llm,
        generation_policy=generation_policy,
        presentation_policy=presentation_policy,
    )

    logger.info(response)


if __name__ == "__main__":
    main()