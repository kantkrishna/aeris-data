# src/production/finops_telemetry.py
"""
FinOps Cost Tracking Telemetry.

Captures execution latency and attributes simulated operational costs
to specific workload tags for platform chargebacks.

Exported Classes:
    FinOpsTracker: Decorator-based workload timer and cost aggregator.
"""

import time
import sqlite3
from typing import Callable, Any, Dict, TypeVar, cast
from functools import wraps

T = TypeVar("T", bound=Callable[..., Any])


class FinOpsTracker:
    def __init__(self, conn: sqlite3.Connection, cost_per_ms: float = 0.001) -> None:
        self.conn = conn
        self.cost_per_ms = cost_per_ms
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS finops_log (
                tag TEXT, duration_ms REAL, cost REAL
            )
        """)

    def track_workload(self, tag: str) -> Callable[[T], T]:
        def decorator(func: T) -> T:
            @wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                start = time.perf_counter()
                result = func(*args, **kwargs)
                end = time.perf_counter()

                duration_ms = (end - start) * 1000
                cost = duration_ms * self.cost_per_ms
                self.conn.execute(
                    "INSERT INTO finops_log VALUES (?, ?, ?)", (tag, duration_ms, cost)
                )
                return result

            return cast(T, wrapper)

        return decorator

    def get_cost_attribution(self) -> Dict[str, float]:
        rows = self.conn.execute(
            "SELECT tag, SUM(cost) FROM finops_log GROUP BY tag"
        ).fetchall()
        return {row[0]: row[1] for row in rows}
