from application.models import FinalAnswerResponse
from day05_context_to_answer.answer_generator import generate_answer
from day06_semantic_validation.semantic_verifier import verify_answer
from day07_claim_citation_alignment.claim_citation_aligner import align_claims_to_citations
from day08_presentation.decide import decide_presentation
from day08_presentation.models import PresentationMode


def answer_query_with_policy(
    *,
    context_pack,
    llm,
    generation_policy,
    presentation_policy,
) -> FinalAnswerResponse:

    # -------------------------
    # Day 5 — Generate answer
    # -------------------------
    answer = generate_answer(
        context_pack=context_pack,
        llm=llm,
        policy=generation_policy,
    )

    # 🚨 EARLY EXIT: generation refusal
    if answer.refusal_reason is not None:
        return FinalAnswerResponse(
            allowed=False,
            mode=PresentationMode.SUPPRESSED,
            answer_text=None,
            citations=None,
            refusal_reason=answer.refusal_reason,
            presentation_reason=None,
        )

    # -------------------------
    # Day 6 — Semantic validation
    # -------------------------
    verification_report = verify_answer(
        answer_text=answer.text,
        context_pack=context_pack,
        llm=llm,
    )

    claims = verification_report.claims
    claim_results = verification_report.claim_results

    # -------------------------
    # Day 7 — Citation alignment
    # -------------------------
    citation_results = align_claims_to_citations(
        claims=claims,
        sentence_text_to_citation_ids=answer.sentence_text_to_citation_ids,
        context_pack=context_pack,
    )

    # -------------------------
    # Day 8 — Presentation gate
    # -------------------------
    decision = decide_presentation(
        policy=presentation_policy,
        claim_results=claim_results,
        citation_results=citation_results,
    )

    if not decision.allowed:
        return FinalAnswerResponse(
            allowed=False,
            mode=decision.mode,
            answer_text=None,
            citations=None,
            refusal_reason=None,
            presentation_reason=decision.reason,
        )

    return FinalAnswerResponse(
        allowed=True,
        mode=decision.mode,
        answer_text=answer.text,
        citations=answer.citations,
        refusal_reason=None,
        presentation_reason=decision.reason,
    )