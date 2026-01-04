# day09_observability/recorder.py

from typing import List, Optional
from datetime import datetime
from day09_observability.models import DecisionTrace, PipelineStats
from day08_presentation.models import PresentationMode


class TraceRecorder:
    """
    Pure observability sink.
    Stores already-built DecisionTrace objects.
    """

    _traces: List[DecisionTrace] = []

    @classmethod
    def record(cls, trace: DecisionTrace) -> None:
        cls._traces.append(trace)

    @classmethod
    def get_all(cls) -> List[DecisionTrace]:
        return list(cls._traces)

    @classmethod
    def clear(cls) -> None:
        cls._traces.clear()