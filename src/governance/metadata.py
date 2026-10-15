# src/governance/metadata.py
"""
Unified Metadata Extraction Model.

Normalizes tags and properties from disparate compute engines into
the AERIS standard format (US-16.1).
"""

from typing import Dict, Any


def normalize_metadata(engine: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extracts and normalizes metadata payload into AERIS unified format."""
    normalized: Dict[str, Any] = {
        "engine": engine,
        "aeris_owner_id": "UNASSIGNED",
        "is_pii": False,
        "compliant": False,
    }

    if engine == "snowflake":
        tags = payload.get("tags", {})
        if not tags:
            return normalized
        normalized["aeris_owner_id"] = tags.get("OWNER", "UNASSIGNED")
        normalized["is_pii"] = tags.get("SENSITIVITY") == "PII"

    elif engine == "databricks":
        props = payload.get("properties", {})
        if not props:
            return normalized
        normalized["aeris_owner_id"] = props.get("owner_id", "UNASSIGNED")
        normalized["is_pii"] = str(props.get("pii_flag")).lower() == "true"

    normalized["compliant"] = normalized["aeris_owner_id"] != "UNASSIGNED"
    return normalized
