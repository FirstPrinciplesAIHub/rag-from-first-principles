from dataclasses import dataclass
from enum import Enum


class ExtraneousCitationPolicy(str, Enum):
    """
    How to treat extra citations that do not support the claim.
    """
    ALLOW = "allow"      # pass with warning
    FAIL = "fail"        # fail alignment


@dataclass(frozen=True)
class AlignmentPolicy:
    """
    Policy controlling claim ↔ citation alignment strictness.
    """

    # How to handle extra (non-supporting) citations
    extraneous_citation_policy: ExtraneousCitationPolicy = (
        ExtraneousCitationPolicy.ALLOW
    )