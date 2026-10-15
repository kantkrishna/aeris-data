# src/production/reliable_ingestion.py
"""
Reliable CDC Data Ingestion Engine.

This module provides an idempotent data ingestion pipeline capable of handling
Change Data Capture (CDC) logs, deduplicating incoming batches, resolving
late-arriving data based on timestamps, and safely evolving target schemas.

Exported Classes:
    ReliableIngestionEngine: Handles CDC merging and schema evolution.
    CDCError: Exception for CDC processing failures.
"""

import csv
import sqlite3
from typing import List, Dict, Any, Tuple


class CDCError(Exception):
    pass


class ReliableIngestionEngine:
    def __init__(self, db_path: str) -> None:
        self.conn = sqlite3.connect(db_path)

    def ingest_cdc(
        self,
        file_path: str,
        table_name: str,
        pk_cols: List[str],
        ts_col: str,
        op_col: str,
    ) -> None:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = list(csv.reader(f))

        if len(reader) < 2:
            return

        headers = reader[0]
        data = reader[1:]

        # 1. Deduplicate within the batch (keep latest ts_col per pk_cols)
        pk_indices = [headers.index(pk) for pk in pk_cols]
        ts_index = headers.index(ts_col)
        op_index = headers.index(op_col)

        latest_records: Dict[Tuple[str, ...], List[str]] = {}
        for row in data:
            pk_val = tuple(row[i] for i in pk_indices)
            if (
                pk_val not in latest_records
                or row[ts_index] > latest_records[pk_val][ts_index]
            ):
                latest_records[pk_val] = row

        deduped_data = list(latest_records.values())

        with self.conn:
            self._ensure_table_and_schema(table_name, headers, pk_cols)

            for row in deduped_data:
                pk_vals = tuple(row[i] for i in pk_indices)
                ts_val = row[ts_index]
                op_val = row[op_index]

                # Check existing timestamp to prevent stale updates
                existing = self._get_existing_record(
                    table_name, pk_cols, pk_vals, ts_col
                )
                if existing and existing >= ts_val:
                    continue  # Ignore stale data

                if op_val == "DELETE":
                    self._execute_delete(table_name, pk_cols, pk_vals)
                else:
                    self._execute_upsert(table_name, headers, row, pk_cols, op_col)

    def _ensure_table_and_schema(
        self, table_name: str, headers: List[str], pk_cols: List[str]
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        if not cursor.fetchone():
            cols = ", ".join([f"{h} TEXT" for h in headers if h != "op"])
            pk_def = ", ".join(pk_cols)
            cursor.execute(
                f"CREATE TABLE {table_name} ({cols}, PRIMARY KEY ({pk_def}))"
            )
        else:
            # Schema Evolution: Add missing columns
            cursor.execute(f"PRAGMA table_info({table_name})")
            existing_cols = {row[1] for row in cursor.fetchall()}
            for h in headers:
                if h not in existing_cols and h != "op":
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {h} TEXT")

    def _get_existing_record(
        self, table_name: str, pk_cols: List[str], pk_vals: Tuple[str, ...], ts_col: str
    ) -> Any:
        where_clause = " AND ".join([f"{col} = ?" for col in pk_cols])
        cursor = self.conn.cursor()
        try:
            res = cursor.execute(
                f"SELECT {ts_col} FROM {table_name} WHERE {where_clause}", pk_vals
            ).fetchone()
            return res[0] if res else None
        except sqlite3.OperationalError:
            return None

    def _execute_delete(
        self, table_name: str, pk_cols: List[str], pk_vals: Tuple[str, ...]
    ) -> None:
        where_clause = " AND ".join([f"{col} = ?" for col in pk_cols])
        self.conn.execute(f"DELETE FROM {table_name} WHERE {where_clause}", pk_vals)

    def _execute_upsert(
        self,
        table_name: str,
        headers: List[str],
        row: List[str],
        pk_cols: List[str],
        op_col: str,
    ) -> None:
        target_headers = [h for h in headers if h != op_col]
        target_vals = [row[headers.index(h)] for h in target_headers]

        cols_str = ", ".join(target_headers)
        placeholders = ", ".join(["?"] * len(target_headers))
        pk_def = ", ".join(pk_cols)

        updates = ", ".join(
            [f"{h}=excluded.{h}" for h in target_headers if h not in pk_cols]
        )
        update_clause = f"DO UPDATE SET {updates}" if updates else "DO NOTHING"

        query = f"INSERT INTO {table_name} ({cols_str}) VALUES ({placeholders}) ON CONFLICT({pk_def}) {update_clause}"
        self.conn.execute(query, target_vals)
