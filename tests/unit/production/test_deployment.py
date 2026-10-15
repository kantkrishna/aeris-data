# tests/unit/production/test_deployment.py
"""
Environment Promotion & Rollback Tests.

Validates the deployment manager's ability to copy states between isolated
environments (e.g., Staging to Prod) and safely roll back to a prior state.
"""

import pytest
from pathlib import Path
from src.production.deployment import EnvironmentManager


def test_deploy_to_production_and_rollback(tmp_path: Path) -> None:
    """US-9.2: Deploy copies staging to prod; rollback reverts to previous state."""
    staging_db = tmp_path / "aeris_staging.db"
    prod_db = tmp_path / "aeris_prod.db"
    staging_db.write_text("staging state 1")

    manager = EnvironmentManager(str(staging_db), str(prod_db))

    # 1. Deploy Staging -> Prod
    manager.deploy()
    assert prod_db.exists()
    assert prod_db.read_text() == "staging state 1"

    # 2. Update staging and deploy again
    staging_db.write_text("staging state 2")
    manager.deploy()
    assert prod_db.read_text() == "staging state 2"

    # 3. Rollback
    manager.rollback()
    assert prod_db.read_text() == "staging state 1"


def test_rollback_without_backup(tmp_path: Path) -> None:
    """US-9.2: Rollback exits cleanly when no previous version exists."""
    manager = EnvironmentManager(str(tmp_path / "stg.db"), str(tmp_path / "prd.db"))
    with pytest.raises(RuntimeError, match="No backup available"):
        manager.rollback()
