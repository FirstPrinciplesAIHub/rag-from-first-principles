from day11_ci_locking.models import CIResult


def enforce_ci(ci_result: CIResult) -> None:
    """
    Hard CI gate.
    """

    if not ci_result.passed:
        raise RuntimeError(
            "CI FAILED:\n\n" + ci_result.report
        )