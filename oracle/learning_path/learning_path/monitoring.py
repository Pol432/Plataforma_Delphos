"""
monitoring.py — Metrics and performance tracking for the LPO.
"""

import time
import logging
from contextlib import contextmanager
from collections import defaultdict

logger = logging.getLogger("lpo.monitoring")
_metrics: dict = defaultdict(list)


@contextmanager
def timer(label: str):
    """Context manager that logs elapsed time for any block."""
    start = time.perf_counter()
    yield
    elapsed_ms = (time.perf_counter() - start) * 1000
    _metrics[label].append(elapsed_ms)
    logger.debug("⏱  %s: %.1fms", label, elapsed_ms)
    if elapsed_ms > 5000:
        logger.warning("SLOW: %s took %.1fms (target <5000ms)", label, elapsed_ms)


def get_metrics() -> dict:
    """Return avg/min/max for all recorded timings."""
    return {
        label: {
            "count": len(vals),
            "avg_ms": round(sum(vals) / len(vals), 1),
            "min_ms": round(min(vals), 1),
            "max_ms": round(max(vals), 1),
        }
        for label, vals in _metrics.items()
    }


def reset_metrics():
    _metrics.clear()
