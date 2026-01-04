# infrastructure/llm/base.py

from abc import ABC, abstractmethod
from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass

@dataclass
class LLMUsage:
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost_usd: float


class LLM(ABC):
    """
    Abstract LLM interface.

    All LLM implementations (FakeLLM, OpenAILLM, BedrockLLM, etc.)
    MUST implement this interface.

    The pipeline must depend ONLY on this interface.
    """

    @abstractmethod
    def generate(
        self,
        *,
        prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """
        Generate text from a prompt.

        Must be:
        - deterministic in tests (FakeLLM)
        - non-deterministic in production (real LLM)
        """
        raise NotImplementedError
    
    
    def get_last_usage(self) -> Optional[LLMUsage]:
        """
        Optional observability hook.
        Default: no usage info.
        """
        return None