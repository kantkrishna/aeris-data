# tests/unit/data-platform/test_log_masking.py
"""
Execution Credential Masking Tests.

Validates US-19.2 logic to explicitly mask injected credentials in
observability logs prior to persistence.
"""

from src.observability.logging import mask_secrets


def test_mask_connection_string() -> None:
    """Given a log with a connection string, passwords are replaced with ***."""
    log_msg = "Connecting to database: postgresql://user:mySecret123@host:5432/db"
    masked = mask_secrets(log_msg)
    assert "mySecret123" not in masked
    assert "postgresql://user:***@host:5432/db" in masked


def test_no_secrets_in_payload() -> None:
    """Given a payload without secrets, the original string is returned unmodified."""
    log_msg = "Executing query SELECT * FROM table;"
    assert mask_secrets(log_msg) == log_msg
