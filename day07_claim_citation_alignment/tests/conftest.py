import pytest

from day06_semantic_validation.claims import Claim
from day04_retrieval_to_context.build_context import ContextPack
from day04_retrieval_to_context.build_context import ContextPolicy



class DummyChunk:
    def __init__(self, chunk_id: str, text: str):
        self.chunk_id = chunk_id
        self.text = text
        
@pytest.fixture
def sample_context_policy():
    return ContextPolicy()


@pytest.fixture
def sample_context_pack(sample_context_policy):
    return ContextPack(
        query="test query",
        policy=sample_context_policy,
        approved_chunks=[],
        dropped_chunks=[],
        is_valid=True,
        invalid_reason=None,
    )


@pytest.fixture
def make_chunk():
    def _make_chunk(chunk_id: str, text: str):
        return DummyChunk(
            chunk_id=chunk_id,
            text=text,
        )
    return _make_chunk