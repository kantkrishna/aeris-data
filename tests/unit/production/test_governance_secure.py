# tests/unit/production/test_governance_secure.py
"""
Secure Governance & Audit Logging Tests.

Validates strict RBAC boundaries, restricted table protection,
and the creation of immutable query audit logs.
"""

import sqlite3
import pytest
from typing import Generator
from src.production.governance_secure import SecureGovernanceEngine


@pytest.fixture
def gov_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE dim_customers (id TEXT)")
    conn.execute("CREATE TABLE hr_salary_data (id TEXT, salary INT)")
    yield conn
    conn.close()


def test_audit_logging_and_least_privilege(gov_db: sqlite3.Connection) -> None:
    """US-10.1: Log all queries and strictly block HR data for analysts."""
    engine = SecureGovernanceEngine(gov_db)
    engine.grant_role("alice", "ANALYST")

    # Valid query is logged
    engine.execute_query("alice", "SELECT * FROM dim_customers")
    logs = gov_db.execute(
        "SELECT username, role, query_text FROM gov_audit_log"
    ).fetchall()
    assert len(logs) == 1
    assert logs[0] == ("alice", "ANALYST", "SELECT * FROM dim_customers")

    # Unauthorized query is blocked and logged
    with pytest.raises(PermissionError, match="Access Denied"):
        engine.execute_query("alice", "SELECT * FROM hr_salary_data")

    logs_after = gov_db.execute(
        "SELECT status FROM gov_audit_log ORDER BY id DESC LIMIT 1"
    ).fetchone()
    assert logs_after[0] == "DENIED"
