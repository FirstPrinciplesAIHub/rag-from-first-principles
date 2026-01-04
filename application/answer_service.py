from application.models import FinalAnswerResponse
from day05_context_to_answer.answer_generator import generate_answer
from day06_semantic_validation.semantic_verifier import verify_answer
from day07_claim_citation_alignment.claim_citation_aligner import align_claims_to_citations
from day08_presentation.decide import decide_presentation
from day08_presentation.models import PresentationMode
from day09_observability.builder import build_decision_trace
from day09_observability.recorder import TraceRecorder
from day09_observability.models import PipelineStats
from day07_claim_citation_alignment.models import AlignmentStatus


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

    # -------------------------
    # EARLY REFUSAL (Day 5)
    # -------------------------
    if answer.refusal_reason is not None:
        trace = build_decision_trace(
            query_text=context_pack.query,

            # Day 4
            context_valid=context_pack.is_valid,
            context_failure_reason=context_pack.invalid_reason,

            # Day 5
            answer_refusal_reason=answer.refusal_reason,

            # Downstream skipped
            entailment_passed=None,
            entailment_failure_code=None,
            citation_alignment_passed=None,

            presentation_mode=None,
            presentation_reason=None,
        )

        TraceRecorder.record(trace)

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

    claims = verification_report.claim_results

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
        claim_results=claims,
        citation_results=citation_results,
    )

    # -------------------------
    # Build stats (Day 09 input)
    # -------------------------
    stats = PipelineStats(
        approved_chunks=context_pack.stats.get("approved_count"),
        dropped_chunks=context_pack.stats.get("dropped_count"),
        total_context_chars=context_pack.stats.get("total_chars"),
        claim_count=len(claims),
        aligned_citations=sum(
            1 for r in citation_results
            if r.status == AlignmentStatus.ALIGNED
        ),
    )

    # -------------------------
    # Final response
    # -------------------------
    if not decision.allowed:
        response = FinalAnswerResponse(
            allowed=False,
            mode=decision.mode,
            answer_text=None,
            citations=None,
            refusal_reason=None,
            presentation_reason=decision.reason,
        )
    else:
        response = FinalAnswerResponse(
            allowed=True,
            mode=decision.mode,
            answer_text=answer.text,
            citations=answer.citations,
            refusal_reason=None,
            presentation_reason=decision.reason,
        )

    # -------------------------
    # Day 09 — Observability (FINAL)
    # -------------------------
    trace = build_decision_trace(
        query_text=context_pack.query,

        # Day 4
        context_valid=context_pack.is_valid,
        context_failure_reason=context_pack.invalid_reason,

        # Day 5
        answer_refusal_reason=None,

        # Day 6
        entailment_passed=verification_report.passed,
        entailment_failure_code=verification_report.failure_reason,

        # Day 7
        citation_alignment_passed=all(
            r.status == AlignmentStatus.ALIGNED
            for r in citation_results
        ),

        # Day 8
        presentation_mode=response.mode,
        presentation_reason=response.presentation_reason,

        stats=stats,
    )

    TraceRecorder.record(trace)

    return response