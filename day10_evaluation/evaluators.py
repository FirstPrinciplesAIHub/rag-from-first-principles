REGRESSION_PRIORITY = [
    "allowed",
    "presentation_severity",
    "confidence",
]


from typing import List
from day10_evaluation.models import Regression
from day08_presentation.models import PresentationMode


def presentation_severity(mode: PresentationMode) -> float:
    if mode == PresentationMode.FULL:
        return 0.0
    if mode == PresentationMode.WARNING:
        return 0.5
    if mode == PresentationMode.SUPPRESSED:
        return 1.0
    return 0.0


def detect_regressions(
    *,
    previous: List,
    current: List,
) -> List[Regression]:
    regressions: List[Regression] = []

    prev_map = {r.case_id: r for r in previous}
    curr_map = {r.case_id: r for r in current}

    for case_id in prev_map.keys() & curr_map.keys():
        prev = prev_map[case_id]
        curr = curr_map[case_id]

        detected: List[Regression] = []

        # 1️⃣ Allowed regression (highest priority)
        if prev.trace.allowed and not curr.trace.allowed:
            detected.append(
                Regression(
                    case_id=case_id,
                    metric="allowed",
                    baseline_value=1.0,
                    current_value=0.0,
                    delta=-1.0,
                )
            )

        # 2️⃣ Presentation severity regression (only if allowed unchanged)
        elif prev.trace.allowed and curr.trace.allowed:
            prev_sev = presentation_severity(prev.trace.presentation_mode)
            curr_sev = presentation_severity(curr.trace.presentation_mode)

            if curr_sev > prev_sev:
                detected.append(
                    Regression(
                        case_id=case_id,
                        metric="presentation_severity",
                        baseline_value=prev_sev,
                        current_value=curr_sev,
                        delta=curr_sev - prev_sev,
                    )
                )

        # 3️⃣ Confidence regression (only if behavior unchanged)
        if not detected:
            if curr.confidence < prev.confidence:
                detected.append(
                    Regression(
                        case_id=case_id,
                        metric="confidence",
                        baseline_value=prev.confidence,
                        current_value=curr.confidence,
                        delta=curr.confidence - prev.confidence,
                    )
                )

        # 🔒 Emit ONLY the highest-priority regression
        if detected:
            regressions.append(detected[0])

    return regressions