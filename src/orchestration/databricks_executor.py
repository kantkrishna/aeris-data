# src/orchestration/databricks_executor.py
"""
Live Databricks Executor.

Implements US-21.1 & 21.2. Orchestrates Databricks jobs and asynchronously
polls for their terminal states. Retrieves error logs dynamically on failure.
"""

import json
import asyncio
from typing import Dict, Any
from databricks.sdk import WorkspaceClient
from databricks.sdk.core import DatabricksError

from src.security.secrets import SecretsManager
from src.exceptions.core import AerisWorkloadException, TransientNetworkError
from src.utils.decorators import retry_with_backoff


class LiveDatabricksExecutor:
    def __init__(self, secrets_manager: SecretsManager):
        self.secrets = secrets_manager

    @retry_with_backoff(retries=3, base_delay=2.0)
    async def execute(self, payload: str) -> Dict[str, Any]:
        """Parses job_id from JSON payload, triggers job, and polls state asynchronously."""
        try:
            payload_data = json.loads(payload)
            job_id = payload_data["job_id"]
        except (json.JSONDecodeError, KeyError) as e:
            raise AerisWorkloadException(
                f"Malformed Databricks payload. Expected JSON with 'job_id'. {e}"
            )

        try:
            client = WorkspaceClient(
                host=self.secrets.get_secret("DATABRICKS_HOST"),
                token=self.secrets.get_secret("DATABRICKS_TOKEN"),
            )

            # Initiate job and extract run_id (bind() returns unblocked run response)
            run = client.jobs.run_now(job_id=job_id).bind()
            run_id = run.run_id

            # Asynchronous Polling Mechanism
            while True:
                run_status = client.jobs.get_run(run_id)
                lifecycle_state = run_status.state.life_cycle_state.value

                if lifecycle_state in ["PENDING", "RUNNING"]:
                    await asyncio.sleep(5)  # Yield thread
                    continue

                if lifecycle_state == "TERMINATED":
                    result_state = run_status.state.result_state.value
                    if result_state == "SUCCESS":
                        return {
                            "status": "success",
                            "run_id": run_id,
                            "engine_used": "databricks",
                        }
                    else:
                        error_msg = run_status.state.state_message
                        raise AerisWorkloadException(
                            f"Databricks Job Failed (Run ID: {run_id}): {error_msg}"
                        )

                if lifecycle_state in ["SKIPPED", "INTERNAL_ERROR", "CANCELED"]:
                    raise AerisWorkloadException(
                        f"Job terminated with abnormal state: {lifecycle_state}"
                    )

        except DatabricksError as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise AerisWorkloadException(
                    f"Databricks Job ID {job_id} not found: {str(e)}"
                ) from e
            raise TransientNetworkError(f"Databricks API Error: {str(e)}") from e
