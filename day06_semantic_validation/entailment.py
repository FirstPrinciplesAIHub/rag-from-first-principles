from dataclasses import dataclass
from enum import Enum
from typing import List
from day02_document_to_chunks.chunker import Chunk

# Import Chunk from wherever it currently lives
# Example:
# from context_pack import Chunk


class EntailmentLabel(str, Enum):
    ENTAILED = "entailed"
    NOT_ENTAILED = "not_entailed"
    UNKNOWN = "unknown"


@dataclass
class EntailmentResult:
    """
    Result of checking whether a claim is supported by context.
    """
    claim_text: str
    label: EntailmentLabel
    rationale: str
    supporting_chunk_ids: List[str]


def check_entailment(
    *,
    claim_text: str,
    context_chunks: List[Chunk],
    llm,
) -> EntailmentResult:
    """
    Determine whether a claim is entailed by the provided context.

    Rules:
    - Judge ONLY based on the provided context
    - Do NOT use outside knowledge
    - Do NOT soften missing evidence
    """

    if not context_chunks:
        return EntailmentResult(
            claim_text=claim_text,
            label=EntailmentLabel.NOT_ENTAILED,
            rationale="No context provided to support the claim.",
            supporting_chunk_ids=[],
        )

    prompt = _build_entailment_prompt(
        claim_text=claim_text,
        context_chunks=context_chunks,
    )

    print("DEBUG PROMPT:\n", prompt)
    response = llm(prompt)

    return _parse_entailment_response(
        claim_text=claim_text,
        response=response,
        context_chunks=context_chunks,
    )

# -------------------------
# Prompt
# -------------------------

def _build_entailment_prompt(
    *,
    claim_text: str,
    context_chunks: List["Chunk"],
) -> str:
    """
    Strict entailment prompt.
    """

    context_block = "\n\n".join(
        f"[{chunk.chunk_id}]\n{chunk.text}"
        for chunk in context_chunks
    )

    return f"""
You are a strict factual verifier.

TASK:
Determine whether the CLAIM is fully supported by the CONTEXT.

RULES:
- Use ONLY the information in the context
- Do NOT use prior knowledge
- If the context does not clearly support the claim, answer NOT_ENTAILED
- Do NOT explain beyond the required format

CONTEXT:
{context_block}

CLAIM:
{claim_text}

RESPONSE FORMAT (must be exact):
LABEL: <ENTAILED | NOT_ENTAILED | UNKNOWN>
RATIONALE: <one sentence>
SUPPORTING_CHUNKS: <comma-separated chunk_ids or NONE>
""".strip()


# -------------------------
# Response parsing
# -------------------------

def _parse_entailment_response(
    *,
    claim_text: str,
    response: str,
    context_chunks: List[Chunk],
) -> EntailmentResult:
    """
    Parse LLM response into EntailmentResult.
    """

    lines = [l.strip() for l in response.splitlines() if l.strip()]
    data = {}

    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip().upper()] = value.strip()

    raw_label = data.get("LABEL", "").strip()

    # Accept ONLY exact labels
    if raw_label == "ENTAILED":
        label = EntailmentLabel.ENTAILED
    elif raw_label == "NOT_ENTAILED":
        label = EntailmentLabel.NOT_ENTAILED
    elif raw_label == "UNKNOWN":
        label = EntailmentLabel.UNKNOWN
    else:
        # Covers cases like "<ENTAILED | NOT_ENTAILED | UNKNOWN>"
        label = EntailmentLabel.UNKNOWN

    rationale = data.get("RATIONALE", "")

    supporting_raw = data.get("SUPPORTING_CHUNKS", "")
    if supporting_raw.upper() == "NONE" or not supporting_raw:
        supporting_chunk_ids = []
    else:
        supporting_chunk_ids = [
            cid.strip()
            for cid in supporting_raw.split(",")
            if cid.strip()
        ]

    return EntailmentResult(
        claim_text=claim_text,
        label=label,
        rationale=rationale,
        supporting_chunk_ids=supporting_chunk_ids,
    )