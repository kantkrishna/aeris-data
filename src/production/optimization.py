# src/production/optimization.py
"""
Query Optimization & FinOps Experiments.

Demonstrates the business value of engineering optimization by replacing
inefficient cross-joins with optimized indexed joins.

Exported Functions:
    run_inefficient_query: Simulates an unoptimized cartesian product.
    run_optimized_query: Executes an optimized inner join.
"""

import time
import sqlite3


def run_inefficient_query(conn: sqlite3.Connection) -> float:
    """Executes a slow cross-join simulation."""
    start = time.perf_counter()
    # Unoptimized cross join logic
    conn.execute(
        "SELECT COUNT(*) FROM t1 CROSS JOIN t2 WHERE t1.id = t2.ref_id"
    ).fetchall()
    return time.perf_counter() - start


def run_optimized_query(conn: sqlite3.Connection) -> float:
    """Executes an optimized join using indexes."""
    conn.execute("CREATE INDEX IF NOT EXISTS idx_t2_ref ON t2(ref_id)")
    start = time.perf_counter()
    conn.execute(
        "SELECT COUNT(*) FROM t1 INNER JOIN t2 ON t1.id = t2.ref_id"
    ).fetchall()
    return time.perf_counter() - start
