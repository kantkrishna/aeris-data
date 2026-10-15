# tests/integration/conftest.py
"""
Integration Test Fixtures and Idempotent Teardown.

Implements US-23.1 and US-23.2. Provides secure fixture injection and 
idempotent teardown mechanisms (DROP TABLE, Cancel Job) protecting
live Sandbox environments from CI/CD drift.
"""
import pytest
import os
from dotenv import load_dotenv
import snowflake.connector # type: ignore
from databricks.sdk import WorkspaceClient # type: ignore

# Ensure .env is loaded for test context
load_dotenv()

@pytest.fixture(scope="session")
def setup_snowflake_test_env():
    """Provides a live Snowflake connection and tears down test artifacts."""
    account = os.environ.get("SNOWFLAKE_ACCOUNT")
    if not account:
        pytest.skip("Skipping live Snowflake integration test: SNOWFLAKE_ACCOUNT not set in environment.")

    conn = snowflake.connector.connect(
        user=os.environ.get("SNOWFLAKE_USER"),
        password=os.environ.get("SNOWFLAKE_PASS"),
        account=account,
        warehouse=os.environ.get("SNOWFLAKE_WH"),
        database=os.environ.get("SNOWFLAKE_DB")
    )
    
    yield conn

    # Idempotent Teardown (US-23.2)
    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS test_aeris_integration;")
    conn.close()

@pytest.fixture(scope="session")
def setup_databricks_test_env():
    """Provides a Databricks WorkspaceClient and handles dangling job runs."""
    host = os.environ.get("DATABRICKS_HOST")
    if not host:
        pytest.skip("Skipping live Databricks integration test: DATABRICKS_HOST not set in environment.")

    client = WorkspaceClient(
        host=host,
        token=os.environ.get("DATABRICKS_TOKEN")
    )
    
    # Pass client to test context
    yield client
    
    # Idempotent Teardown (US-23.2)
    test_job_id = os.environ.get("DATABRICKS_TEST_JOB_ID")
    if test_job_id:
        active_runs = client.jobs.list_runs(job_id=int(test_job_id), active_only=True)
        for run in active_runs:
            client.jobs.cancel_run(run.run_id)