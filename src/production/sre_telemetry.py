# src/production/sre_telemetry.py
"""
SRE Observability and Telemetry Engine.

Extends standard telemetry to track Service Level Objectives (SLOs), calculate
error budgets, and automatically map system exceptions to diagnostic runbooks.

Exported Classes:
    SRETelemetryLogger: Handles advanced metrics and runbook assignments.

Module Attributes:
    RUNBOOK_MAP (dict): Maps exception class names to Markdown documentation.
"""

import sqlite3
from typing import Optional, Dict
from datetime import datetime

RUNBOOK_MAP = {
    "DataQualityError": "docs/runbooks/dq_failure.md",
    "IngestionError": "docs/runbooks/ingestion_failure.md",
    "CDCError": "docs/runbooks/cdc_failure.md",
}
DEFAULT_RUNBOOK = "docs/runbooks/general_triage.md"


class SRETelemetryLogger:
    def __init__(self, conn: sqlite3.Connection, target_slo: float = 0.95) -> None:
        self.conn = conn
        self.target_slo = target_slo
        self._init_schema()

    def _init_schema(self) -> None:
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS ops_audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    job_name TEXT,
                    status TEXT,
                    error_msg TEXT,
                    runbook_url TEXT
                )
            """)

    def log_run(
        self, job_name: str, status: str, error: Optional[Exception] = None
    ) -> None:
        error_msg = str(error) if error else None
        runbook_url = None

        if status == "FAILED" and error:
            error_type = type(error).__name__
            runbook_url = RUNBOOK_MAP.get(error_type, DEFAULT_RUNBOOK)

        with self.conn:
            self.conn.execute(
                "INSERT INTO ops_audit_log (timestamp, job_name, status, error_msg, runbook_url) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), job_name, status, error_msg, runbook_url),
            )

    def get_sre_metrics(self) -> Dict[str, float]:
        cursor = self.conn.cursor()
        total = cursor.execute("SELECT COUNT(*) FROM ops_audit_log").fetchone()[0]
        successes = cursor.execute(
            "SELECT COUNT(*) FROM ops_audit_log WHERE status='SUCCESS'"
        ).fetchone()[0]

        if total == 0:
            return {
                "total_runs": 0.0,
                "success_rate": 100.0,
                "error_budget_remaining": 100.0,
            }

        failures = total - successes
        rate = (successes / total) * 100

        # Allowed failures based on target SLO
        allowed_failures = total * (1.0 - self.target_slo)
        remaining_budget = allowed_failures - failures

        return {
            "total_runs": float(total),
            "success_rate": rate,
            "error_budget_remaining": remaining_budget,
        }
