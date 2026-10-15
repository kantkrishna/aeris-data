# tests/unit/data-platform/test_orchestrator.py
"""
Orchestration Abstraction Tests.

Validates US-13.2 abstract execution interface. Ensures workloads
route to Snowflake or Databricks correctly without leaking engine
logic into the parent caller.
"""

import pytest
from src.orchestration.executor import (
    ExecuteWorkload,
    UnsupportedEngineException,
    MalformedWorkloadException,
)


def test_snowflake_execution() -> None:
    """Given engine='snowflake' and valid payload, trigger Snowflake execution."""
    result = ExecuteWorkload(engine="snowflake", payload="CALL sp_transform()").run()
    assert result["status"] == "success"
    assert result["engine_used"] == "snowflake"


def test_databricks_execution() -> None:
    """Given engine='databricks' and valid payload, trigger Databricks job."""
    result = ExecuteWorkload(engine="databricks", payload="job_id_12345").run()
    assert result["status"] == "success"
    assert result["engine_used"] == "databricks"


def test_unsupported_engine() -> None:
    """Given unsupported engine, raise UnsupportedEngineException."""
    with pytest.raises(UnsupportedEngineException):
        ExecuteWorkload(engine="redshift", payload="SELECT 1").run()


def test_missing_payload() -> None:
    """Given None payload, raise MalformedWorkloadException."""
    with pytest.raises(MalformedWorkloadException):
        ExecuteWorkload(engine="snowflake", payload=None).run()  # type: ignore
