from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class RetrievedChunk:
    """
    Raw retrieval candidate.

    This is NOT trusted.
    Judgment happens in Day 4.
    """
    text: str
    score: float
    metadata: Dict