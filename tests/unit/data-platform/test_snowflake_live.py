# tests/unit/data-platform/test_snowflake_live.py
"""
Live Snowflake Executor Tests.

Validates US-20.1 (execution) and US-20.2 (exception mapping) via the Python Connector.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.orchestration.snowflake_executor import LiveSnowflakeExecutor
from src.exceptions.core import AerisWorkloadException, AerisEngineTimeoutException


@pytest.fixture
def mock_secrets() -> MagicMock:
    secrets = MagicMock()
    secrets.get_secret.return_value = "mock_value"
    return secrets


@pytest.mark.asyncio
@patch("src.orchestration.snowflake_executor.snowflake.connector.connect")
async def test_successful_snowflake_execution(
    mock_connect: MagicMock, mock_secrets: MagicMock
) -> None:
    """Given valid credentials, it authenticates, executes, closes, and returns row counts."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.rowcount = 5
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_connect.return_value.__enter__.return_value = mock_conn

    executor = LiveSnowflakeExecutor(mock_secrets)
    result = await executor.execute("UPDATE table SET x = 1;")

    assert result["status"] == "success"
    assert result["rows_processed"] == 5
    mock_cursor.execute.assert_called_once_with("UPDATE table SET x = 1;")


@pytest.mark.asyncio
@patch("src.orchestration.snowflake_executor.snowflake.connector.connect")
async def test_snowflake_exception_mapping(
    mock_connect: MagicMock, mock_secrets: MagicMock
) -> None:
    """Given engine specific exceptions, they map to standard AERIS exceptions."""
    from snowflake.connector.errors import ProgrammingError, OperationalError

    # Test ProgrammingError -> AerisWorkloadException
    mock_connect.side_effect = ProgrammingError("Syntax Error")
    executor = LiveSnowflakeExecutor(mock_secrets)
    with pytest.raises(AerisWorkloadException):
        await executor.execute("SELECT * FRO table;")

    # Test OperationalError -> AerisEngineTimeoutException
    mock_connect.side_effect = OperationalError("Connection Timeout")
    with pytest.raises(AerisEngineTimeoutException):
        await executor.execute("SELECT 1;")
