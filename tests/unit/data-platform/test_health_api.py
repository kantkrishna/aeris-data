# tests/unit/data-platform/test_health_api.py
"""
Unified Health Metrics API Tests.

Validates US-16.2 API endpoints returning unified status from both engines.
"""

from fastapi.testclient import TestClient
from src.observability.api import app

import pytest

client = TestClient(app)


def test_unified_health_metrics() -> None:
    """Validates 200 OK and combined payload structure."""
    response = client.get("/health/unified")
    assert response.status_code == 200
    data = response.json()
    assert "snowflake" in data
    assert "databricks" in data
    assert data["snowflake"]["status"] == "healthy"
    assert data["databricks"]["status"] == "healthy"


def test_partial_degradation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Validates 206 Partial Content when one engine API times out."""
    # Mocking Databricks engine failure
    monkeypatch.setenv("SIMULATE_DB_FAILURE", "true")
    response = client.get("/health/unified")
    assert response.status_code == 206
    data = response.json()
    assert data["databricks"]["status"] == "unavailable"
