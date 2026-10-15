# src/production/resilience.py
"""
Pipeline Resilience and Reliability Utilities.

Provides decorators and wrappers to ensure automated retries for transient
system failures, increasing overall pipeline robustness.

Exported Functions:
    with_retries: Decorator to retry functions on failure.

Module Attributes:
    MaxRetriesExceeded: Raised when retry limits are exhausted.
"""

import time
from functools import wraps
from typing import Callable, Any, TypeVar, cast

T = TypeVar("T", bound=Callable[..., Any])


class MaxRetriesExceeded(Exception):
    pass


def with_retries(max_retries: int = 3, delay: float = 1.0) -> Callable[[T], T]:
    def decorator(func: T) -> T:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempts = 0
            while attempts <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts > max_retries:
                        raise MaxRetriesExceeded(
                            f"Failed after {max_retries} retries: {str(e)}"
                        ) from e
                    time.sleep(delay)
            return None

        return cast(T, wrapper)

    return decorator
