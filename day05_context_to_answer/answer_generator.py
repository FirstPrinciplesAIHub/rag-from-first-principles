# day05_context_to_answer/answer_generator.py
from infrastructure.llm.base import LLM
from .schemas import Answer, Citation
from .policies import GenerationPolicy
from .prompt import render_prompt
from .citation_validator import validate_citations


def generate_answer(*, context_pack, llm:LLM, policy: GenerationPolicy) -> Answer:
    # --------------------------------------------------
    # Backward-compatible context validity
    # --------------------------------------------------
    is_valid = getattr(context_pack, "is_valid", True)
    invalid_reason = getattr(context_pack, "invalid_reason", None)

    if policy.refuse_if_no_context and not is_valid:
        return Answer(
            text="I don't have enough information to answer.",
            citations=[],
            sentence_text_to_citation_ids={},
            refusal_reason=invalid_reason or "empty_context",
        )

    # --------------------------------------------------
    # BACKWARD COMPATIBILITY LAYER (CRITICAL)
    # --------------------------------------------------
    if hasattr(context_pack, "context_text"):
        # Legacy Day-05 FakeContextPack
        context_text = context_pack.context_text.strip()
        sources = getattr(context_pack, "sources", [])
    else:
        # New ContextPack
        approved_chunks = getattr(context_pack, "approved_chunks", [])
        context_text = "\n\n".join(
            chunk["text"] for chunk in approved_chunks
        ).strip()
        sources = [
            chunk.get("metadata", {}).get("source")
            for chunk in approved_chunks
            if chunk.get("metadata", {}).get("source") is not None
        ]

    # --------------------------------------------------
    # Empty context refusal (MUST happen before citations)
    # --------------------------------------------------
    if policy.refuse_if_no_context and not context_text:
        return Answer(
            text="I don't have enough information to answer.",
            citations=[],
            sentence_text_to_citation_ids={},
            refusal_reason="empty_context",
        )

    # --------------------------------------------------
    # Render prompt
    # --------------------------------------------------
    prompt = render_prompt(
        context_text=context_text,
        query=context_pack.query,
        sources=sources,
    )

    raw = llm.generate(
        prompt=prompt,
        max_tokens=policy.max_answer_tokens,
        temperature=policy.temperature,
    )

    text = raw.strip()

    # --------------------------------------------------
    # Model-level refusal
    # --------------------------------------------------
    if "don't have enough information" in text.lower():
        return Answer(
            text=text,
            citations=[],
            sentence_text_to_citation_ids={},
            refusal_reason=None,
        )

    # --------------------------------------------------
    # Citation enforcement (Day-05 responsibility)
    # --------------------------------------------------
    if not validate_citations(
        answer_text=text,
        allowed_sources=sources,
    ):
        return Answer(
            text="I don't have enough information to answer.",
            citations=[],
            sentence_text_to_citation_ids={},
            refusal_reason="missing_or_invalid_citations",
        )

    # --------------------------------------------------
    # Successful answer
    # --------------------------------------------------
    return Answer(
        text=text,
        citations=sources,
        sentence_text_to_citation_ids={},
        refusal_reason=None,
    )