# src/orchestration/executor.py
"""
Abstract Execution Layer.

Provides polymorphic engine execution. Handles routing of data workloads
to the appropriate compute engine while abstracting connectivity and
authentication logic from the caller.

Classes:
    ExecuteWorkload: Factory and runner for workloads.
    SnowflakeExecutor: Concrete implementation for Snowflake.
    DatabricksExecutor: Concrete implementation for Databricks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class UnsupportedEngineException(Exception):
    pass


class MalformedWorkloadException(Exception):
    pass


class BaseExecutor(ABC):
    @abstractmethod
    def execute(self, payload: str) -> Dict[str, str]:
        pass


class SnowflakeExecutor(BaseExecutor):
    def execute(self, payload: str) -> Dict[str, str]:
        # Implementation interacts with snowflake.connector
        return {"status": "success", "engine_used": "snowflake"}


class DatabricksExecutor(BaseExecutor):
    def execute(self, payload: str) -> Dict[str, str]:
        # Implementation interacts with databricks-sdk
        return {"status": "success", "engine_used": "databricks"}


class ExecuteWorkload:
    def __init__(self, engine: str, payload: Optional[str]):
        if payload is None:
            raise MalformedWorkloadException("Payload cannot be None.")
        self.engine = engine.lower()
        self.payload = payload

    def run(self) -> Dict[str, str]:
        if self.engine == "snowflake":
            return SnowflakeExecutor().execute(self.payload)
        elif self.engine == "databricks":
            return DatabricksExecutor().execute(self.payload)
        else:
            raise UnsupportedEngineException(f"Engine {self.engine} is not supported.")
