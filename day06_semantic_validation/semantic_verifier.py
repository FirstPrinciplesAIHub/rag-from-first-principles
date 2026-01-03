from dataclasses import dataclass
from typing import List

from .claims import Claim, extract_claims
from .entailment import (
    check_entailment,
    EntailmentResult,
    EntailmentLabel,
)

# Import ContextPack from wherever it currently lives
# Example:
# from context_pack import ContextPack


@dataclass
class VerificationReport:
    """
    Final semantic verification outcome for an answer.
    """
    passed: bool
    claim_results: List[EntailmentResult]
    failure_reason: str = None


def verify_answer(
    *,
    answer_text: str,
    context_pack,
    llm,
) -> VerificationReport:
    """
    Verify that ALL factual claims in the answer
    are entailed by the cited context.
    """
    
    claims = extract_claims(answer_text)

    if not claims:
        # No claims → nothing to verify → pass
        return VerificationReport(
            passed=True,
            claim_results=[],
            failure_reason=None,
        )

    entailment_results: List[EntailmentResult] = []

    for claim in claims:
        context_chunks = _get_context_for_claim(
            claim=claim,
            context_pack=context_pack,
        )

        # 🚨 NO CONTEXT → FAIL (but record result)
        if not context_chunks:
            result = EntailmentResult(
                claim_text=claim.text,
                label=EntailmentLabel.NOT_ENTAILED,
                rationale="No approved context available to support this claim.",
                supporting_chunk_ids=[],
            )

            entailment_results.append(result)

            return VerificationReport(
                passed=False,
                claim_results=entailment_results,
                failure_reason=(
                    f"No approved context for claim: '{claim.text}'"
                ),
            )

        result = check_entailment(
            claim_text=claim.text,
            context_chunks=context_chunks,
            llm=llm,
        )

        entailment_results.append(result)

        # 🚨 ANY NON-ENTAILED → FAIL
        if result.label != EntailmentLabel.ENTAILED:
            return VerificationReport(
                passed=False,
                claim_results=entailment_results,
                failure_reason=(
                    f"Claim not entailed: '{claim.text}' "
                    f"(label={result.label})"
                ),
            )

    return VerificationReport(
        passed=True,
        claim_results=entailment_results,
        failure_reason=None,
    )


# -------------------------
# Context mapping
# -------------------------

def _get_context_for_claim(
    *,
    claim: Claim,
    context_pack,
):
    """
    Retrieve context chunks allowed for entailment.

    Day 6 rule:
    - Use approved context ONLY
    - Do not retrieve or expand
    """

    context_chunks = []

    for entry in context_pack.approved_chunks:
        # Case 1: wrapped Chunk object
        if "chunk" in entry:
            context_chunks.append(entry["chunk"])
            continue

        # Case 2: flat dict with text (fallback)
        if "text" in entry and "chunk_id" in entry:
            from dataclasses import dataclass

            @dataclass
            class _AdHocChunk:
                chunk_id: str
                text: str

            context_chunks.append(
                _AdHocChunk(
                    chunk_id=entry["chunk_id"],
                    text=entry["text"],
                )
            )
    
    return context_chunks