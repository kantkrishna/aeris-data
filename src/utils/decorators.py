# src/utils/decorators.py
"""
Resiliency Decorators.

Implements US-22.1. Provides an asynchronous exponential backoff wrapper
that intelligently differentiates between transient platform errors and
fatal workload errors.
"""

import asyncio
import functools
from typing import Callable, Any
from src.exceptions.core import (
    TransientNetworkError,
    AerisWorkloadException,
    AerisInfrastructureException,
)


def retry_with_backoff(retries: int = 3, base_delay: float = 1.0) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while attempt <= retries:
                try:
                    return await func(*args, **kwargs)
                except AerisWorkloadException as e:
                    # Non-transient error, fail immediately
                    raise e
                except TransientNetworkError as e:
                    attempt += 1
                    if attempt > retries:
                        raise AerisInfrastructureException(
                            f"Exhausted retries due to: {str(e)}"
                        ) from e
                    await asyncio.sleep(base_delay * (2 ** (attempt - 1)))

        return wrapper

    return decorator
