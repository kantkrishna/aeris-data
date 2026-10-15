# tests/unit/production/test_finops.py
"""
FinOps Telemetry & Cost Attribution Tests.

Validates the tracking of workload duration and the calculation
of attributed costs based on workload tags.
"""

import sqlite3
import time
import pytest
from typing import Generator
from src.production.finops_telemetry import FinOpsTracker


@pytest.fixture
def finops_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_workload_cost_tracking(finops_db: sqlite3.Connection) -> None:
    """US-11.1: Tracks execution time and applies cost by tag."""
    tracker = FinOpsTracker(finops_db, cost_per_ms=0.001)

    @tracker.track_workload("ai_training")
    def mock_ai_workload() -> None:
        time.sleep(0.05)  # 50ms

    mock_ai_workload()

    costs = tracker.get_cost_attribution()
    assert "ai_training" in costs
    assert costs["ai_training"] > 0.04  # ~ $0.05 based on sleep
