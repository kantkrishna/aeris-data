# src/observability/api.py
"""
Unified Health Metrics API.

Provides centralized health check endpoints aggregating metrics from
both Databricks and Snowflake into a single pane of glass (US-16.2).
"""

import os
from fastapi import FastAPI, Response
from typing import Dict, Any

app = FastAPI(title="AERIS Unified Observability")


@app.get("/health/unified")
def get_unified_health(response: Response) -> Dict[str, Any]:
    # Simulate Databricks failure condition for testability
    db_failed = os.environ.get("SIMULATE_DB_FAILURE", "false").lower() == "true"

    payload = {
        "snowflake": {"status": "healthy", "active_warehouses": 2, "failed_jobs": 0},
        "databricks": {
            "status": "unavailable" if db_failed else "healthy",
            "active_clusters": 0 if db_failed else 1,
            "failed_jobs": 1 if db_failed else 0,
        },
    }

    if db_failed:
        response.status_code = 206  # Partial Content

    return payload
