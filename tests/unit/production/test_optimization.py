# tests/unit/production/test_optimization.py
"""
FinOps Workload Optimization Tests.

Proves the FinOps loop by validating that an optimized query executes
in less than 50% of the time of a poorly constructed query.
"""

import sqlite3
import pytest
from typing import Generator
from src.production.optimization import run_inefficient_query, run_optimized_query


@pytest.fixture
def query_db() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(":memory:")
    # Seed large mock data
    conn.execute("CREATE TABLE t1 (id INT, val TEXT)")
    conn.execute("CREATE TABLE t2 (id INT, ref_id INT)")
    conn.executemany(
        "INSERT INTO t1 VALUES (?, ?)", [(i, f"A{i}") for i in range(1000)]
    )
    conn.executemany(
        "INSERT INTO t2 VALUES (?, ?)", [(i, i % 100) for i in range(1000)]
    )
    yield conn
    conn.close()


def test_query_optimization(query_db: sqlite3.Connection) -> None:
    """US-11.2: Optimized query takes < 50% time of inefficient query."""
    old_time = run_inefficient_query(query_db)
    new_time = run_optimized_query(query_db)

    assert new_time < (old_time * 0.5), "Optimization did not reduce cost by 50%"
