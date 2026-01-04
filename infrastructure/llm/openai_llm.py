from typing import Optional
from infrastructure.llm.pricing import estimate_cost
from openai import OpenAI
from infrastructure.llm.base import LLM, LLMUsage

class OpenAILLM(LLM):
    def __init__(self, model: str, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self._last_usage: Optional[LLMUsage]= None

    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )

        usage = response.usage

        self._last_usage = LLMUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            cost_usd=estimate_cost(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            ),
        )

        return response.choices[0].message.content

    def get_last_usage(self):
        return self._last_usage

