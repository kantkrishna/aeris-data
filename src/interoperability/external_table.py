# src/interoperability/external_table.py
"""
Interoperability DDL Generator.

Generates SQL commands to enable Snowflake to read externally hosted
Delta/Iceberg tables managed by Databricks, satisfying US-15.1.
"""


def generate_external_table_ddl(
    table_name: str, location: str, refresh_only: bool = False
) -> str:
    """Generates DDL string for Snowflake external table execution."""
    if refresh_only:
        return f"ALTER EXTERNAL TABLE {table_name} REFRESH;"

    return f"""
    CREATE EXTERNAL TABLE {table_name}
    WITH LOCATION = '{location}'
    FILE_FORMAT = (TYPE = PARQUET);
    """
