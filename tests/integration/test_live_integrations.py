# tests/integration/test_live_integrations.py
"""
Live Environment Integration Tests.

Validates the full execution chain implemented in Epics 20-22 against
live Sandbox environments (US-23.1).
"""

import pytest
from src.security.secrets import EnvVarSecretsProvider
from src.orchestration.snowflake_executor import LiveSnowflakeExecutor


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_snowflake_execution(setup_snowflake_test_env):
    """Given live credentials, Snowflake executes query and teardown removes it."""
    # Assumes valid live env vars exist
    secrets = EnvVarSecretsProvider()
    executor = LiveSnowflakeExecutor(secrets)

    # Create temp state to prove write access
    await executor.execute("CREATE OR REPLACE TABLE test_aeris_integration (id INT);")

    # Execute actual query validation
    result = await executor.execute("SELECT CURRENT_VERSION();")

    assert result["status"] == "success"
    # Note: Teardown DROP TABLE occurs automatically in conftest.py yield
