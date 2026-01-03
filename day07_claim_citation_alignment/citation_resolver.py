from typing import Dict, List

from day04_retrieval_to_context.build_context import ContextPack
from day02_document_to_chunks.chunker import Chunk as ContextChunk


class CitationResolutionError(Exception):
    """Base error for citation resolution failures."""


class InvalidCitationError(CitationResolutionError):
    """Raised when a citation ID does not exist in approved context."""


class DroppedCitationError(CitationResolutionError):
    """Raised when a citation refers to a dropped (unapproved) chunk."""


def resolve_citations(
    citation_ids: List[str],
    context_pack: ContextPack,
) -> Dict[str, ContextChunk]:
    """
    Resolve citation IDs to approved ContextChunks.

    Rules:
    - Citation ID must exist in approved_chunks
    - Dropped chunks are NOT allowed
    - Resolution is deterministic

    Returns:
        Dict[citation_id, ContextChunk]

    Raises:
        InvalidCitationError
        DroppedCitationError
    """

    resolved: Dict[str, ContextChunk] = {}

    approved_chunks = {
        chunk.chunk_id: chunk
        for chunk in context_pack.approved_chunks
    }

    dropped_chunk_ids = {
        chunk.chunk_id
        for chunk in context_pack.dropped_chunks
    }

    for cid in citation_ids:
        if cid in approved_chunks:
            resolved[cid] = approved_chunks[cid]
            continue

        if cid in dropped_chunk_ids:
            raise DroppedCitationError(
                f"Citation '{cid}' refers to a dropped context chunk."
            )

        raise InvalidCitationError(
            f"Citation '{cid}' does not exist in approved context."
        )

    return resolved