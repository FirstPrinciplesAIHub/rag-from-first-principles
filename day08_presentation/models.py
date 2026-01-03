from enum import Enum


class PresentationMode(Enum):
    FULL = "full"                 # show answer normally
    WARNING = "warning"           # show answer + warning banner
    SUPPRESSED = "suppressed"     # do not show answer
    DEBUG = "debug"               # internal/audit view
    
    
    
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PresentationDecision:
    allowed: bool
    mode: PresentationMode
    reason: Optional[str] = None
    

@dataclass(frozen=True)
class PresentationPolicy:
    allow_partial: bool = False
    allow_warnings: bool = True
    debug_mode: bool = False
    
    
