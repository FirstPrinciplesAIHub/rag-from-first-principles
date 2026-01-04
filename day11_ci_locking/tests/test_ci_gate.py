import pytest

from day11_ci_locking.ci_gate import enforce_ci
from day11_ci_locking.models import CIResult


def test_ci_passes_when_no_regressions():
    result = CIResult(
        passed=True,
        regressions=[],
        report="OK",
    )

    enforce_ci(result)  # should not raise


def test_ci_fails_on_regression():
    result = CIResult(
        passed=False,
        regressions=["fake_regression"],
        report="REGRESSION DETECTED",
    )

    with pytest.raises(RuntimeError):
        enforce_ci(result)