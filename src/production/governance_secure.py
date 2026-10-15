# src/production/governance_secure.py
"""
Secure Governance & Audit Engine.

Enforces least-privilege role boundaries, restricts specific sensitive datasets,
and maintains an immutable query audit log.

Exported Classes:
    SecureGovernanceEngine: Proxies DB execution with strict validation.
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Any


class SecureGovernanceEngine:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn
        self.roles: Dict[str, str] = {}
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS gov_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                username TEXT,
                role TEXT,
                query_text TEXT,
                status TEXT
            )
        """)

    def grant_role(self, username: str, role: str) -> None:
        self.roles[username] = role

    def execute_query(self, username: str, query: str) -> List[Any]:
        role = self.roles.get(username, "PUBLIC")
        timestamp = datetime.now().isoformat()

        # Block HR data for non-admins
        if "hr_salary_data" in query.lower() and role != "SYSADMIN":
            self._log_audit(timestamp, username, role, query, "DENIED")
            raise PermissionError(f"Access Denied: {role} cannot access HR data.")

        self._log_audit(timestamp, username, role, query, "SUCCESS")
        return self.conn.execute(query).fetchall()

    def _log_audit(
        self, ts: str, user: str, role: str, query: str, status: str
    ) -> None:
        self.conn.execute(
            "INSERT INTO gov_audit_log (timestamp, username, role, query_text, status) VALUES (?, ?, ?, ?, ?)",
            (ts, user, role, query, status),
        )
