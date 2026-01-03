from dataclasses import dataclass
from typing import Optional

from day08_presentation.models import PresentationMode

from typing import Optional

refusal_reason: Optional[str]
@dataclass
class FinalAnswerResponse:
    allowed: bool
    mode: PresentationMode
    answer_text: Optional[str]
    citations: Optional[list]
    refusal_reason: Optional[str]
    presentation_reason: Optional[str]