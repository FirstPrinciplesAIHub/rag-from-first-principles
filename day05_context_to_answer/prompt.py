def render_prompt(*, context_text: str, query: str, sources: list[str]) -> str:
    sources_block = "\n".join(f"- {s}" for s in sources)

    return f"""You are a question-answering system.

You must follow ALL rules below:
- Use ONLY the provided context.
- Every factual statement MUST include at least one citation.
- Citations must be copied EXACTLY from the allowed sources list.
- Use citation format: [source_id]
- If the answer is not present in the context, say:
  "I don't have enough information to answer."

Allowed sources:
---------------
{sources_block}
---------------

Context:
---------
{context_text}
---------

Question:
{query}

Answer:
"""