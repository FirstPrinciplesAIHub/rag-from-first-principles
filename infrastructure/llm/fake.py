from infrastructure.llm.base import LLM, LLMUsage

class FakeLLM(LLM):
    def __init__(self, fixed_response: str):
        self.fixed_response = fixed_response
        self._usage = LLMUsage(
            prompt_tokens=10,
            completion_tokens=10,
            total_tokens=20,
            cost_usd=0.0,
        )

    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        return self.fixed_response

    def get_last_usage(self):
        return LLMUsage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0,
            cost_usd=0.0,
        )