from day10_evaluation.models import Regression
from day10_evaluation.reports import generate_regression_report


def test_no_regressions_report():
    report = generate_regression_report([])
    assert "NO REGRESSIONS" in report
    assert "CI STATUS: PASS" in report


def test_blocking_regression_report():
    regressions = [
        Regression(
            case_id="case_allowed",
            metric="allowed",
            baseline_value=1.0,
            current_value=0.0,
            delta=-1.0,
        )
    ]

    report = generate_regression_report(regressions)

    assert "REGRESSION DETECTED" in report
    assert "case_allowed" in report
    assert "Metric: allowed" in report
    assert "CI STATUS: FAIL" in report