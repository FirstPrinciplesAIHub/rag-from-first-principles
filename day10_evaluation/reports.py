from typing import List
from day10_evaluation.models import Regression


BLOCKING_METRICS = {"allowed"}


def generate_regression_report(
    regressions: List[Regression],
) -> str:
    if not regressions:
        return (
            "✅ NO REGRESSIONS DETECTED\n\n"
            "CI STATUS: PASS\n"
        )

    # ---------------- Summary ----------------
    cases = sorted({r.case_id for r in regressions})
    blocking = [
        r for r in regressions if r.metric in BLOCKING_METRICS
    ]

    lines: List[str] = []

    lines.append("❌ REGRESSION DETECTED")
    lines.append(f"Cases affected: {len(cases)}")
    lines.append(f"Blocking regressions: {len(blocking)}")
    lines.append("")

    # ---------------- Per-case details ----------------
    by_case = {}
    for r in regressions:
        by_case.setdefault(r.case_id, []).append(r)

    for case_id in sorted(by_case.keys()):
        lines.append(f"Case: {case_id}")

        for r in by_case[case_id]:
            lines.append(f"  - Metric: {r.metric}")
            lines.append(f"    Baseline: {r.baseline_value}")
            lines.append(f"    Current:  {r.current_value}")
            lines.append(f"    Delta:    {r.delta:+.2f}")

        lines.append("")

    # ---------------- CI verdict ----------------
    if blocking:
        lines.append("CI STATUS: FAIL")
        lines.append("Reason: Blocking regressions detected")
    else:
        lines.append("CI STATUS: WARN")
        lines.append("Reason: Non-blocking regressions detected")

    return "\n".join(lines)