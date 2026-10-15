# src/production/deployment.py
"""
Environment Promotion Manager.

This module handles the physical promotion of database state across environments
and maintains backups for rapid rollbacks.

Exported Classes:
    EnvironmentManager: Deploys and rolls back state files.
"""

import shutil
import os
from pathlib import Path


class EnvironmentManager:
    def __init__(self, staging_path: str, prod_path: str) -> None:
        self.staging = Path(staging_path)
        self.prod = Path(prod_path)
        self.backup = Path(str(prod_path) + ".bak")

    def deploy(self) -> None:
        if self.prod.exists():
            shutil.copy2(self.prod, self.backup)
        if self.staging.exists():
            shutil.copy2(self.staging, self.prod)

    def rollback(self) -> None:
        if not self.backup.exists():
            raise RuntimeError("No backup available to rollback.")
        shutil.copy2(self.backup, self.prod)
        os.remove(self.backup)
