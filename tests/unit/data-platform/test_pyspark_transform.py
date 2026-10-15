# tests/unit/data-platform/test_pyspark_transform.py
"""
PySpark Workload Transformation Tests.

Validates US-14.2 databricks PySpark logic. Uses standard data structures
to verify transformation rules before executing on an actual Spark cluster.
"""

import pytest
from typing import List, Dict, Any
from src.transformations.spark_workload import (
    transform_shipments,
    SchemaValidationException,
)


def test_valid_pyspark_transformation() -> None:
    """Validates PySpark transformation logic output."""
    mock_input: List[Dict[str, Any]] = [
        {"shipment_id": "S1", "base_cost": 100.0, "tax": 10.0}
    ]
    output = transform_shipments(mock_input)
    assert len(output) == 1
    assert output[0]["total_cost"] == 110.0


def test_empty_dataframe() -> None:
    """Validates empty data handles gracefully."""
    output = transform_shipments([])
    assert len(output) == 0


def test_malformed_schema() -> None:
    """Validates missing required columns throws custom Exception."""
    mock_input = [{"shipment_id": "S2", "base_cost": 100.0}]  # Missing tax
    with pytest.raises(SchemaValidationException):
        transform_shipments(mock_input)
