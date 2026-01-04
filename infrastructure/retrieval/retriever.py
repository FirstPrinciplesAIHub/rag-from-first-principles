from typing import List
from infrastructure.retrieval.models import RetrievedChunk


def retrieve_chunks(query: str) -> List[dict]:
    """
    TEMPORARY retriever.

    This will later be replaced by:
    - embeddings
    - vector DB
    - hybrid retrieval

    For now, this is deterministic and testable.
    """

    # 🔴 Stub data (example corpus)
    corpus = [
        RetrievedChunk(
            text="Refunds are processed within 5–7 business days.",
            score=0.92,
            metadata={"source": "policy_doc"},
        ),
        RetrievedChunk(
            text="Welcome to our company handbook.",
            score=0.12,
            metadata={"source": "boilerplate"},
        ),
    ]

    # Return as dicts to match existing pipeline expectations
    return [
        {
            "text": c.text,
            "score": c.score,
            "metadata": c.metadata,
        }
        for c in corpus
    ]