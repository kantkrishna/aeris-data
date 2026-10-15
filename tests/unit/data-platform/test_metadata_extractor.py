# tests/unit/data-platform/test_metadata_extractor.py
"""
Unified Governance Metadata Tests.

Validates US-16.1 extraction pipeline that normalizes Snowflake and
Databricks metadata tags into a common AERIS JSON metadata model.
"""

from src.governance.metadata import normalize_metadata


def test_snowflake_metadata_extraction() -> None:
    """Validates mapping of Snowflake tags to unified model."""
    sf_mock = {
        "object_type": "TABLE",
        "tags": {"OWNER": "team_alpha", "SENSITIVITY": "PII"},
    }
    result = normalize_metadata("snowflake", sf_mock)
    assert result["aeris_owner_id"] == "team_alpha"
    assert result["is_pii"] is True
    assert result["engine"] == "snowflake"


def test_databricks_metadata_extraction() -> None:
    """Validates mapping of Databricks Unity Catalog tags to unified model."""
    db_mock = {
        "table_type": "MANAGED",
        "properties": {"owner_id": "team_alpha", "pii_flag": "true"},
    }
    result = normalize_metadata("databricks", db_mock)
    assert result["aeris_owner_id"] == "team_alpha"
    assert result["is_pii"] is True
    assert result["engine"] == "databricks"


def test_missing_tags_handled() -> None:
    """Validates non-compliant objects do not crash the pipeline."""
    result = normalize_metadata("snowflake", {"tags": {}})
    assert result["aeris_owner_id"] == "UNASSIGNED"
    assert result["compliant"] is False
