import os

from infrastructure.llm.base import LLM
from infrastructure.llm.fake import FakeLLM
from infrastructure.llm.openai_llm import OpenAILLM


def build_llm() -> LLM:
    env = os.getenv("RAG_ENV", "test")

    if env == "test":
        return FakeLLM(
            fixed_response="This answer is grounded in the context."
        )

    if env == "prod":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is required when RAG_ENV=prod")

        return OpenAILLM(
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            api_key=api_key,
        )

    raise RuntimeError(f"Unknown RAG_ENV: {env}")