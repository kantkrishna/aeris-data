# tests/unit/data-platform/test_interoperability.py
"""
Cross-Engine Data Access Tests.

Validates US-15.1 external table query generation and RBAC simulation
for cross-engine interoperability between Databricks and Snowflake.
"""

from src.interoperability.external_table import generate_external_table_ddl


def test_external_table_ddl_generation() -> None:
    """Validates creation of DDL to read Delta tables from Snowflake."""
    ddl = generate_external_table_ddl(
        table_name="databricks_shipments", location="s3://aeris-delta/shipments/"
    )
    assert "CREATE EXTERNAL TABLE" in ddl
    assert "s3://aeris-delta/shipments/" in ddl


def test_schema_refresh_command() -> None:
    """Validates generation of the refresh command for schema evolution."""
    command = generate_external_table_ddl(
        table_name="databricks_shipments", location="", refresh_only=True
    )
    assert command == "ALTER EXTERNAL TABLE databricks_shipments REFRESH;"
