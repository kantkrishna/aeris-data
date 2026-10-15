# tests/unit/data-platform/test_retry_backoff.py
"""
Resiliency and Exponential Backoff Tests.

Validates US-22.1 exponential backoff decorator for transient API failures
and instant failure behavior for workload exceptions.
"""

import pytest
from unittest.mock import AsyncMock
from src.utils.decorators import retry_with_backoff
from src.exceptions.core import (
    TransientNetworkError,
    AerisWorkloadException,
    AerisInfrastructureException,
)


@pytest.mark.asyncio
async def test_retry_transient_success() -> None:
    """Given a transient error, retry executes and eventually succeeds."""
    mock_func = AsyncMock(
        side_effect=[
            TransientNetworkError("Timeout"),
            TransientNetworkError("Timeout"),
            "Success",
        ]
    )

    @retry_with_backoff(retries=3, base_delay=0.01)
    async def resilient_call() -> str:
        return await mock_func()

    result = await resilient_call()
    assert result == "Success"
    assert mock_func.call_count == 3


@pytest.mark.asyncio
async def test_immediate_failure_on_workload_exception() -> None:
    """Given a non-transient error, decorator fails immediately without retrying."""
    mock_func = AsyncMock(side_effect=AerisWorkloadException("Syntax Error"))

    @retry_with_backoff(retries=3, base_delay=0.01)
    async def resilient_call() -> str:
        return await mock_func()

    with pytest.raises(AerisWorkloadException):
        await resilient_call()
    assert mock_func.call_count == 1


@pytest.mark.asyncio
async def test_exhausted_retries_raises_infrastructure_error() -> None:
    """Given constant transient errors, decorator exhausts retries and raises infrastructure exception."""
    mock_func = AsyncMock(side_effect=TransientNetworkError("Timeout"))

    @retry_with_backoff(retries=2, base_delay=0.01)
    async def resilient_call() -> str:
        return await mock_func()

    with pytest.raises(AerisInfrastructureException):
        await resilient_call()
    assert mock_func.call_count == 3  # 1 initial + 2 retries
