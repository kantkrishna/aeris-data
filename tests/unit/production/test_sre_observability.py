# tests/unit/production/test_sre_observability.py
"""
Epic 8 Tests: SRE & Observability.

Validates the calculation of SLOs and error budgets, as well as the
automatic mapping of exceptions to operational runbooks in telemetry.
"""

import pytest
import sqlite3
from typing import Generator

from src.production.sre_telemetry import SRETelemetryLogger


@pytest.fixture
def telemetry_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_slo_and_error_budget_tracking(telemetry_db: sqlite3.Connection) -> None:
    """US-8.1: Track SLO metrics and calculate remaining error budgets."""
    logger = SRETelemetryLogger(telemetry_db)

    # 9 successful runs
    for _ in range(9):
        logger.log_run("ingest_raw", status="SUCCESS")

    # 1 failed run
    logger.log_run("transform", status="FAILED", error=ValueError("Bad data"))

    metrics = logger.get_sre_metrics()

    assert metrics["total_runs"] == 10
    assert metrics["success_rate"] == 90.0

    # Target SLO is 95%. Budget allowed failures for 10 runs = 10 * (1 - 0.95) = 0.5.
    # Actual failures = 1. Error budget should be depleted (negative).
    assert metrics["error_budget_remaining"] < 0


def test_automated_incident_runbooks(telemetry_db: sqlite3.Connection) -> None:
    """US-8.2: Failures are automatically linked to diagnostic runbooks."""
    logger = SRETelemetryLogger(telemetry_db)

    class DataQualityError(Exception):
        pass

    logger.log_run("transform", status="FAILED", error=DataQualityError("Nulls found"))
    logger.log_run("ingest", status="FAILED", error=ConnectionError("Timeout"))

    logs = telemetry_db.execute(
        "SELECT error_msg, runbook_url FROM ops_audit_log ORDER BY id"
    ).fetchall()

    # Mapped exception
    assert "Nulls found" in logs[0][0]
    assert logs[0][1] == "docs/runbooks/dq_failure.md"

    # Fallback runbook
    assert "Timeout" in logs[1][0]
    assert logs[1][1] == "docs/runbooks/general_triage.md"
