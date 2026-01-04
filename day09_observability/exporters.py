# day09_observability/exporters.py

import json
import logging
from dataclasses import asdict
from typing import Optional

from .models import DecisionTrace

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# JSON Exporter
# ---------------------------------------------------------

def export_trace_as_json(
    trace: DecisionTrace,
    *,
    filepath: Optional[str] = None,
) -> None:
    """
    Export a DecisionTrace as JSON.

    Safe to call in production:
    - No mutation
    - Fail-open
    """

    try:
        payload = asdict(trace)

        if filepath:
            with open(filepath, "a") as f:
                f.write(json.dumps(payload) + "\n")
        else:
            logger.info("decision_trace_json=%s", json.dumps(payload))

    except Exception:
        # Observability must never break the pipeline
        logger.exception("Failed to export DecisionTrace as JSON")


# ---------------------------------------------------------
# Logger Exporter (human-readable)
# ---------------------------------------------------------

def export_trace_to_logs(trace: DecisionTrace) -> None:
    """
    Emit a compact, human-readable trace summary to logs.
    """

    try:
        logger.info(
            "RAG_TRACE | allowed=%s | failure_layer=%s | failure_code=%s | mode=%s",
            trace.allowed,
            trace.failure_layer.name if trace.failure_layer else None,
            trace.failure_code.value if trace.failure_code else None,
            trace.presentation_mode.value if trace.presentation_mode else None,
        )

    except Exception:
        logger.exception("Failed to log DecisionTrace")


# ---------------------------------------------------------
# Metrics Exporter (stub)
# ---------------------------------------------------------

def export_trace_to_metrics(trace: DecisionTrace) -> None:
    """
    Hook for metrics systems (Prometheus, OpenTelemetry, etc).

    Intentionally a stub — wiring belongs to infra, not core logic.
    """

    try:
        # Example (pseudo-code):
        #
        # metrics.increment(
        #     "rag.requests.total",
        #     tags={
        #         "allowed": trace.allowed,
        #         "failure_layer": trace.failure_layer.value
        #             if trace.failure_layer else "none",
        #     },
        # )
        pass

    except Exception:
        logger.exception("Failed to export DecisionTrace metrics")