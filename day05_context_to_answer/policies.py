# day05_context_to_answer/policies.py
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationPolicy:
    max_answer_tokens: int = 300
    temperature: float = 0.2
    refuse_if_no_context: bool = True