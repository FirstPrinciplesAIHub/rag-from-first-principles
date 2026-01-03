from typing import Dict, List

from day06_semantic_validation.claims import Claim
from day04_retrieval_to_context.build_context import ContextPack

from day07_claim_citation_alignment.models import (
    AlignmentStatus,
    ClaimCitationResult,
)
from day07_claim_citation_alignment.citation_resolver import (
    resolve_citations,
    InvalidCitationError,
    DroppedCitationError,
)


def _normalize(text: str) -> str:
    return (
        text.lower()
        .replace(".", "")
        .replace(",", "")
        .strip()
    )


def align_claims_to_citations(
    *,
    claims: List[Claim],
    sentence_text_to_citation_ids: Dict[str, List[str]],
    context_pack: ContextPack,
) -> List[ClaimCitationResult]:

    results: List[ClaimCitationResult] = []

    for claim in claims:
        cited_ids = sentence_text_to_citation_ids.get(
            claim.source_sentence, []
        )

        if not cited_ids:
            results.append(
                ClaimCitationResult(
                    claim_text=claim.text,
                    sentence_index=claim.claim_id,
                    cited_ids=[],
                    status=AlignmentStatus.MISSING_CITATION,
                    reason="Claim has no citations.",
                )
            )
            continue

        try:
            resolved = resolve_citations(
                citation_ids=cited_ids,
                context_pack=context_pack,
            )
        except (InvalidCitationError, DroppedCitationError) as e:
            results.append(
                ClaimCitationResult(
                    claim_text=claim.text,
                    sentence_index=claim.claim_id,
                    cited_ids=cited_ids,
                    status=AlignmentStatus.INVALID_CITATION,
                    reason=str(e),
                )
            )
            continue

        supporting_ids = []
        extraneous_ids = []

        for cid, chunk in resolved.items():
            if _normalize(claim.text) in _normalize(chunk.text):
                supporting_ids.append(cid)
            else:
                extraneous_ids.append(cid)

        if not supporting_ids:
            results.append(
                ClaimCitationResult(
                    claim_text=claim.text,
                    sentence_index=claim.claim_id,
                    cited_ids=cited_ids,
                    status=AlignmentStatus.MISALIGNED,
                    reason="None of the cited chunks support this claim.",
                )
            )
            continue

        status = (
            AlignmentStatus.EXTRANEOUS_CITATION
            if extraneous_ids
            else AlignmentStatus.ALIGNED
        )

        results.append(
            ClaimCitationResult(
                claim_text=claim.text,
                sentence_index=claim.claim_id,
                cited_ids=cited_ids,
                status=status,
                supporting_citation_ids=supporting_ids,
                extraneous_citation_ids=extraneous_ids or None,
            )
        )

    return results