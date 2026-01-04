# day09_observability/signals.py

from enum import Enum
from typing import Dict, Set

from .models import FailureCode, PipelineLayer, PresentationMode


# ---------------------------------------------------------
# Canonical layer signal names
# ---------------------------------------------------------

class SignalName(Enum):
    CONTEXT_ACCEPTED = "context_accepted"
    CONTEXT_REJECTED = "context_rejected"

    ANSWER_GENERATED = "answer_generated"
    ANSWER_REFUSED = "answer_refused"

    CLAIMS_VERIFIED = "claims_verified"
    CLAIMS_REJECTED = "claims_rejected"

    CITATIONS_ALIGNED = "citations_aligned"
    CITATIONS_MISALIGNED = "citations_misaligned"

    PRESENTATION_ALLOWED = "presentation_allowed"
    PRESENTATION_WARNING = "presentation_warning"
    PRESENTATION_SUPPRESSED = "presentation_suppressed"


# ---------------------------------------------------------
# Which failure codes are valid for which layer
# (Used for validation, analytics, dashboards)
# ---------------------------------------------------------

LAYER_FAILURE_CODES: Dict[PipelineLayer, Set[FailureCode]] = {
    PipelineLayer.DAY_04_CONTEXT: {
        FailureCode.EMPTY_CONTEXT,
        FailureCode.INSUFFICIENT_CONTEXT,
    },

    PipelineLayer.DAY_05_GENERATION: {
        FailureCode.MISSING_CITATION,
        FailureCode.INVALID_CITATION,
    },

    PipelineLayer.DAY_06_ENTAILMENT: {
        FailureCode.NOT_ENTAILED,
        FailureCode.UNKNOWN_ENTAILMENT,
    },

    PipelineLayer.DAY_07_CITATION_ALIGNMENT: {
        FailureCode.MISALIGNED_CITATION,
        FailureCode.EXTRANEOUS_CITATION,
    },

    PipelineLayer.DAY_08_PRESENTATION: {
        FailureCode.SUPPRESSED_BY_POLICY,
    },
}


# ---------------------------------------------------------
# Presentation mode → signal mapping
# ---------------------------------------------------------

PRESENTATION_MODE_SIGNAL: Dict[PresentationMode, SignalName] = {
    PresentationMode.NORMAL: SignalName.PRESENTATION_ALLOWED,
    PresentationMode.WARNING: SignalName.PRESENTATION_WARNING,
    PresentationMode.SUPPRESSED: SignalName.PRESENTATION_SUPPRESSED,
}


# ---------------------------------------------------------
# Optional human-readable descriptions
# (Safe: diagnostics only, never used for decisions)
# ---------------------------------------------------------

FAILURE_DESCRIPTIONS: Dict[FailureCode, str] = {
    FailureCode.EMPTY_CONTEXT:
        "No admissible context was available after judgment.",

    FailureCode.INSUFFICIENT_CONTEXT:
        "Context was present but insufficient to answer safely.",

    FailureCode.MISSING_CITATION:
        "Answer did not contain required citations.",

    FailureCode.INVALID_CITATION:
        "Answer referenced sources not present in context.",

    FailureCode.NOT_ENTAILED:
        "At least one factual claim was not supported by context.",

    FailureCode.UNKNOWN_ENTAILMENT:
        "Entailment could not be determined with confidence.",

    FailureCode.MISALIGNED_CITATION:
        "Claim meaning did not align with cited source.",

    FailureCode.EXTRANEOUS_CITATION:
        "Citation present but not supporting any claim.",

    FailureCode.SUPPRESSED_BY_POLICY:
        "Answer was suppressed by presentation policy.",
}