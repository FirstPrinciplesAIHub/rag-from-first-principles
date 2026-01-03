from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class AlignmentStatus(str, Enum):
    """
    Possible outcomes of aligning a claim with its citations.
    """
    ALIGNED = "aligned"
    MISSING_CITATION = "missing_citation"
    INVALID_CITATION = "invalid_citation"
    MISALIGNED = "misaligned"
    EXTRANEOUS_CITATION = "extraneous_citation"


@dataclass(frozen=True)
class Citation:
    """
    Represents a single citation reference found in the answer text.
    """
    citation_id: str
    sentence_index: int


@dataclass
class ClaimCitationResult:
    """
    Result of validating one claim against its citations.
    """
    claim_text: str
    sentence_index: int
    cited_ids: List[str]

    status: AlignmentStatus

    # Optional diagnostics
    reason: Optional[str] = None
    supporting_citation_ids: Optional[List[str]] = None
    extraneous_citation_ids: Optional[List[str]] = None