# src/transformations/spark_workload.py
"""
Databricks PySpark Transformation Logic.

Simulates the core logic for the Databricks Spark workload, ensuring
valid schema structures and deterministic cost calculations.
"""

from typing import List, Dict, Any


class SchemaValidationException(Exception):
    pass


def transform_shipments(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforms raw shipment data by calculating total cost.
    In a live cluster, this would utilize pyspark.sql.DataFrame.
    """
    if not data:
        return []

    transformed = []
    for row in data:
        if "base_cost" not in row or "tax" not in row:
            raise SchemaValidationException("Missing required schema columns.")

        row["total_cost"] = row["base_cost"] + row["tax"]
        transformed.append(row)

    return transformed
