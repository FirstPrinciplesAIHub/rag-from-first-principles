# conftest.py (or equivalent)


import pytest
from dataclasses import dataclass


# ----------------------------
# Fake LLM
# ----------------------------

class FakeLLM:
    def __init__(self, fixed_response: str):
        self.fixed_response = fixed_response

    def generate(self, *, prompt, max_tokens, temperature):
        return self.fixed_response


@pytest.fixture
def fake_llm():
    return FakeLLM(
        "Cancellations are allowed within 30 days of purchase. "
        "[policy_a.pdf#section-3]"
    )

# ----------------------------
# Fake ContextPack
# ----------------------------

@dataclass
class FakeContextPack:
    query: str
    context_text: str
    sources: list


@pytest.fixture
def sample_context_pack():
    return FakeContextPack(
        query="What is the cancellation policy?",
        context_text="Cancellations are allowed within 30 days of purchase.",
        sources=["policy_a.pdf#section-3"],
    )


@pytest.fixture
def thin_context_pack():
    return FakeContextPack(
        query="What is the cancellation policy?",
        context_text="This document describes pricing tiers only.",
        sources=["policy_a.pdf#section-1"],
    )


@pytest.fixture
def empty_context_pack():
    return FakeContextPack(
        query="What is the cancellation policy?",
        context_text="",
        sources=[],
    )