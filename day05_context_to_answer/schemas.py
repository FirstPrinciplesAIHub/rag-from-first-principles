# day05_context_to_answer/schemas.py
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Citation:
    source_id: str
    location: Optional[str] = None


@dataclass
class Answer:
    text: str
    citations: List[Citation]
    sentence_text_to_citation_ids: dict[str, list[str]]
    refusal_reason: Optional[str] = None
