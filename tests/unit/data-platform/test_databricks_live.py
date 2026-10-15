# tests/unit/data-platform/test_databricks_live.py
"""
Live Databricks Executor Tests.

Validates US-21.1 (Job Triggers) and US-21.2 (Async Polling & Error Fetching)
utilizing the official databricks-sdk.
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.orchestration.databricks_executor import LiveDatabricksExecutor
from src.exceptions.core import AerisWorkloadException


@pytest.fixture
def mock_secrets() -> MagicMock:
    secrets = MagicMock()
    secrets.get_secret.return_value = "mock_token"
    return secrets


@pytest.mark.asyncio
@patch("src.orchestration.databricks_executor.WorkspaceClient")
async def test_databricks_job_trigger_and_poll_success(
    mock_ws_client: MagicMock, mock_secrets: MagicMock
) -> None:
    """Given a payload with job_id, triggers job, polls state transitions, returns success."""
    mock_ws = mock_ws_client.return_value
    mock_ws.jobs.run_now.return_value.bind.return_value.run_id = 12345

    # Mock sequence of state returns for the polling loop
    mock_run_pending = MagicMock()
    mock_run_pending.state.life_cycle_state.value = "PENDING"
    mock_run_success = MagicMock()
    mock_run_success.state.life_cycle_state.value = "TERMINATED"
    mock_run_success.state.result_state.value = "SUCCESS"

    mock_ws.jobs.get_run.side_effect = [mock_run_pending, mock_run_success]

    executor = LiveDatabricksExecutor(mock_secrets)
    result = await executor.execute(json.dumps({"job_id": 999}))

    assert result["status"] == "success"
    assert result["run_id"] == 12345
    assert mock_ws.jobs.run_now.call_count == 1


@pytest.mark.asyncio
@patch("src.orchestration.databricks_executor.WorkspaceClient")
async def test_databricks_job_poll_failure_fetches_logs(
    mock_ws_client: MagicMock, mock_secrets: MagicMock
) -> None:
    """Given a FAILED terminal state, breaks loop, fetches logs, raises exception."""
    mock_ws = mock_ws_client.return_value
    mock_ws.jobs.run_now.return_value.bind.return_value.run_id = 54321

    mock_run_failed = MagicMock()
    mock_run_failed.state.life_cycle_state.value = "TERMINATED"
    mock_run_failed.state.result_state.value = "FAILED"
    mock_run_failed.state.state_message = "NullPointerException at PySpark line 42"
    mock_ws.jobs.get_run.return_value = mock_run_failed

    executor = LiveDatabricksExecutor(mock_secrets)

    with pytest.raises(AerisWorkloadException) as exc_info:
        await executor.execute(json.dumps({"job_id": 111}))

    assert "NullPointerException at PySpark line 42" in str(exc_info.value)
