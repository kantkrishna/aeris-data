# src/production/repo_linter.py
"""
Structural and Governance Linter.

Extends the repository linter to enforce the presence of Operating Model,
Governance, and Risk Register documentation.

Exported Functions:
    validate_operating_model: Checks directory and document structures.
"""

from pathlib import Path
import re


def validate_operating_model(base_path: Path) -> bool:
    required_files = [
        "docs/governance/access_matrix.md",
        "docs/operating_model/team_boundaries.md",
        "docs/operating_model/roadmap.md",
        "docs/operating_model/risk_register.md",
    ]

    for f in required_files:
        if not (base_path / f).exists():
            return False

    # Validate Risk Register Headers
    content = (base_path / "docs/operating_model/risk_register.md").read_text()
    if not re.search(r"##\s+Risk", content, re.IGNORECASE):
        return False
    if not re.search(r"##\s+Impact", content, re.IGNORECASE):
        return False
    if not re.search(r"##\s+Mitigation", content, re.IGNORECASE):
        return False

    return True
