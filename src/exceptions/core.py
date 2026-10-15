# src/exceptions/core.py
"""
Core AERIS Platform Exceptions.

Provides standard platform exceptions enabling cross-engine abstraction
and deterministic retry logic handling.
"""


class AerisException(Exception):
    pass


class SecretNotFoundException(AerisException):
    pass


class AerisWorkloadException(AerisException):
    """Raised for non-transient workload failures (e.g., SQL syntax, missing schema)."""

    pass


class AerisEngineTimeoutException(AerisException):
    """Raised when the execution engine times out."""

    pass


class AerisInfrastructureException(AerisException):
    """Raised for permanent infrastructure failures or exhausted retries."""

    pass


class TransientNetworkError(AerisException):
    """Raised for transient issues (e.g., HTTP 429, temporary disconnects)."""

    pass
