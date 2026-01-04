# infrastructure/llm/pricing.py

def estimate_cost(
    *,
    prompt_tokens: int,
    completion_tokens: int,
) -> float:
    """
    Estimate OpenAI cost based on token usage.

    Pricing is centralized here so it can be updated
    without touching pipeline logic.
    """

    PRICE_PER_1K_PROMPT = 0.0005
    PRICE_PER_1K_COMPLETION = 0.0015

    return (
        (prompt_tokens / 1000) * PRICE_PER_1K_PROMPT
        + (completion_tokens / 1000) * PRICE_PER_1K_COMPLETION
    )