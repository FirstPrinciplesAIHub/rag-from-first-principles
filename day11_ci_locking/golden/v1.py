from day11_ci_locking.models import GoldenBehavior

from day08_presentation.models import PresentationMode
from day09_observability.models import PipelineLayer, FailureCode

GOLDEN_BEHAVIORS = [
    GoldenBehavior(
        case_id="refund_policy_basic",
        allowed=True,
        presentation_mode=PresentationMode.FULL,
        failure_layer=None,
        failure_code=None,
        confidence=1.0,
    ),

    GoldenBehavior(
        case_id="missing_context_refusal",
        allowed=False,
        presentation_mode=PresentationMode.SUPPRESSED,
        failure_layer=PipelineLayer.DAY_04_CONTEXT,
        failure_code=FailureCode.EMPTY_CONTEXT,
        confidence=0.0,
    ),
]