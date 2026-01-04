from day04_retrieval_to_context.build_context import ContextPolicy, build_context_pack

from infrastructure.retrieval.retriever import retrieve_chunks
def build_context_for_query(
    *,
    query: str,
    policy: ContextPolicy,
):
    retrieved = retrieve_chunks(query)

    approved = []
    dropped = []

    for chunk in retrieved:
        approved.append(
            {
                "text": chunk["text"],
                "metadata": chunk.get("metadata", {}),
                "score": chunk.get("score"),          # OBSERVATION ONLY
                "_reason": "retrieved_candidate",
            }
        )

    return build_context_pack(
        query=query,
        policy=policy,
        approved_chunks=approved,
        dropped_chunks=dropped,
    )