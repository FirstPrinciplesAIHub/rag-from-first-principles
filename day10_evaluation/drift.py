from typing import List
from day10_evaluation.models import EvaluationResult, Regression
from day08_presentation.models import PresentationMode

PRESENTATION_SCORE = {
    PresentationMode.FULL: 0.0,
    PresentationMode.WARNING: 0.5,
    PresentationMode.SUPPRESSED: 1.0,
}


def detect_regressions(
    *,
    previous: List[EvaluationResult],
    current: List[EvaluationResult],
) -> List[Regression]:
    regressions: List[Regression] = []

    prev_map = {r.case_id: r for r in previous}

    for curr in current:
        prev = prev_map.get(curr.case_id)
        if not prev:
            continue

        # ---------- Metric 1: allowed (PRIMARY) ----------
        prev_allowed = 1.0 if prev.response.allowed else 0.0
        curr_allowed = 1.0 if curr.response.allowed else 0.0

        if curr_allowed < prev_allowed:
            regressions.append(
                Regression(
                    case_id=curr.case_id,
                    metric="allowed",
                    baseline_value=prev_allowed,
                    current_value=curr_allowed,
                    delta=curr_allowed - prev_allowed,
                )
            )
            # 🔒 Short-circuit: no secondary regressions matter
            continue

        # ---------- Metric 2: presentation_severity (SECONDARY) ----------
        prev_sev = PRESENTATION_SCORE[prev.response.mode]
        curr_sev = PRESENTATION_SCORE[curr.response.mode]

        if curr_sev > prev_sev:
            regressions.append(
                Regression(
                    case_id=curr.case_id,
                    metric="presentation_severity",
                    baseline_value=prev_sev,
                    current_value=curr_sev,
                    delta=curr_sev - prev_sev,
                )
            )

    return regressions