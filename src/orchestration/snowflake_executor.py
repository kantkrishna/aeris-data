# src/orchestration/snowflake_executor.py
"""
Live Snowflake Executor.

Implements US-20.1 & 20.2. Orchestrates live SQL payloads against Snowflake
using the official python connector. Maps engine-specific exceptions
into standardized platform exceptions.
"""

import asyncio
import snowflake.connector  # type: ignore
from snowflake.connector.errors import ProgrammingError, OperationalError, DatabaseError  # type: ignore
from typing import Dict, Any

from src.security.secrets import SecretsManager
from src.exceptions.core import (
    AerisWorkloadException,
    AerisEngineTimeoutException,
    TransientNetworkError,
)
from src.utils.decorators import retry_with_backoff


class LiveSnowflakeExecutor:
    def __init__(self, secrets_manager: SecretsManager):
        self.secrets = secrets_manager

    @retry_with_backoff(retries=3, base_delay=2.0)
    async def execute(self, payload: str) -> Dict[str, Any]:
        """Authenticates, executes payload, and standardizes exceptions."""

        def _sync_execute() -> Dict[str, Any]:
            try:
                # Use context managers to enforce secure closure
                with snowflake.connector.connect(
                    user=self.secrets.get_secret("SNOWFLAKE_USER"),
                    password=self.secrets.get_secret("SNOWFLAKE_PASS"),
                    account=self.secrets.get_secret("SNOWFLAKE_ACCOUNT"),
                    warehouse=self.secrets.get_secret("SNOWFLAKE_WH"),
                    database=self.secrets.get_secret("SNOWFLAKE_DB"),
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(payload)
                        rows = cursor.rowcount if cursor.rowcount != -1 else 0
                        return {
                            "status": "success",
                            "rows_processed": rows,
                            "engine_used": "snowflake",
                        }

            except ProgrammingError as pe:
                raise AerisWorkloadException(
                    f"Snowflake SQL Syntax/Workload Error: {str(pe)}"
                ) from pe
            except OperationalError as oe:
                # OperationalError often covers timeouts and connection drops
                raise AerisEngineTimeoutException(
                    f"Snowflake Operational/Timeout Error: {str(oe)}"
                ) from oe
            except DatabaseError as de:
                # Treat generic database connection issues as transient network errors
                raise TransientNetworkError(
                    f"Snowflake Connection Issue: {str(de)}"
                ) from de

        # Offload blocking Snowflake library to asyncio thread pool
        return await asyncio.to_thread(_sync_execute)
