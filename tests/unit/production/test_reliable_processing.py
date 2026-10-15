# tests/unit/production/test_reliable_processing.py
"""
Epic 7 Tests: Reliable Data Processing.

Validates CDC ingestion, idempotency, late-arriving data, schema evolution,
and automated retry mechanisms for the production pipeline.
"""

import csv
import pytest
from pathlib import Path
from typing import Generator

from src.production.reliable_ingestion import ReliableIngestionEngine
from src.production.resilience import with_retries, MaxRetriesExceeded


@pytest.fixture
def db_engine() -> Generator[ReliableIngestionEngine, None, None]:
    engine = ReliableIngestionEngine(":memory:")
    yield engine
    engine.conn.close()


def test_idempotent_cdc_ingestion_and_deduplication(
    db_engine: ReliableIngestionEngine, tmp_path: Path
) -> None:
    """US-7.1: Pipeline deduplicates records and processes inserts, updates, and deletes idempotently."""
    file_path = tmp_path / "cdc_batch.csv"
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "val", "updated_at", "op"])
        # Multiple updates to the same ID in one batch (Deduplication)
        writer.writerow(["1", "A", "2023-01-01T10:00:00", "INSERT"])
        writer.writerow(["1", "B", "2023-01-01T10:05:00", "UPDATE"])
        # A delete operation
        writer.writerow(["2", "X", "2023-01-01T10:00:00", "DELETE"])

    # Pre-seed the table to test deletes
    db_engine.conn.execute(
        "CREATE TABLE test_table (id TEXT PRIMARY KEY, val TEXT, updated_at TEXT)"
    )
    db_engine.conn.execute(
        "INSERT INTO test_table VALUES ('2', 'Old', '2023-01-01T09:00:00')"
    )

    db_engine.ingest_cdc(str(file_path), "test_table", ["id"], "updated_at", "op")

    cursor = db_engine.conn.cursor()
    rows = cursor.execute(
        "SELECT id, val, updated_at FROM test_table ORDER BY id"
    ).fetchall()

    # ID 1 should have the latest state 'B', ID 2 should be deleted
    assert len(rows) == 1
    assert rows[0] == ("1", "B", "2023-01-01T10:05:00")

    # Re-running the exact same file should result in no state change (Idempotency)
    db_engine.ingest_cdc(str(file_path), "test_table", ["id"], "updated_at", "op")
    rows_after = cursor.execute(
        "SELECT id, val, updated_at FROM test_table ORDER BY id"
    ).fetchall()
    assert rows == rows_after


def test_late_arriving_data_and_schema_evolution(
    db_engine: ReliableIngestionEngine, tmp_path: Path
) -> None:
    """US-7.2: Pipeline ignores stale updates and dynamically adds new columns."""
    db_engine.conn.execute(
        "CREATE TABLE evolve_table (id TEXT PRIMARY KEY, val TEXT, updated_at TEXT)"
    )
    db_engine.conn.execute(
        "INSERT INTO evolve_table VALUES ('1', 'Newer State', '2023-01-02T10:00:00')"
    )

    file_path = tmp_path / "late_data.csv"
    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        # Stale update (older timestamp), plus a brand new column 'new_col'
        writer.writerow(["id", "val", "updated_at", "op", "new_col"])
        writer.writerow(["1", "Stale State", "2023-01-01T10:00:00", "UPDATE", "X"])
        writer.writerow(["2", "Fresh State", "2023-01-03T10:00:00", "INSERT", "Y"])

    db_engine.ingest_cdc(str(file_path), "evolve_table", ["id"], "updated_at", "op")

    rows = db_engine.conn.execute(
        "SELECT id, val, updated_at, new_col FROM evolve_table ORDER BY id"
    ).fetchall()

    assert len(rows) == 2
    # ID 1 should retain 'Newer State', new column should be NULL for existing records, or ignored on stale update
    assert rows[0] == ("1", "Newer State", "2023-01-02T10:00:00", None)
    # ID 2 should be inserted with the new column value
    assert rows[1] == ("2", "Fresh State", "2023-01-03T10:00:00", "Y")


def test_automated_retry_mechanism() -> None:
    """US-7.3: Transient failures are retried automatically."""
    attempts = 0

    @with_retries(max_retries=2, delay=0.0)
    def flappy_function() -> str:
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise ValueError("Transient network lock")
        return "SUCCESS"

    result = flappy_function()
    assert result == "SUCCESS"
    assert attempts == 2

    attempts = 0

    @with_retries(max_retries=2, delay=0.0)
    def broken_function() -> None:
        nonlocal attempts
        attempts += 1
        raise ValueError("Persistent failure")

    with pytest.raises(MaxRetriesExceeded):
        broken_function()
    assert attempts == 3  # 1 initial + 2 retries
