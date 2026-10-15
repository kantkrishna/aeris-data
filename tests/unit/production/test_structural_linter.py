# tests/unit/production/test_structural_linter.py
"""
Operating Model & Governance Structural Tests.

Validates the presence and format of organizational documentation
(US-10.2, US-12.1, US-12.2).
"""

from pathlib import Path
from src.production.repo_linter import validate_operating_model


def test_validate_operating_model_documents(tmp_path: Path) -> None:
    """US-10.2, US-12.1, US-12.2: Required docs exist and have proper headers."""
    # Create required structure
    (tmp_path / "docs" / "governance").mkdir(parents=True)
    (tmp_path / "docs" / "operating_model").mkdir(parents=True)

    (tmp_path / "docs/governance/access_matrix.md").write_text("# Matrix")
    (tmp_path / "docs/operating_model/team_boundaries.md").write_text("# Teams")
    (tmp_path / "docs/operating_model/roadmap.md").write_text("# Roadmap")

    risk_reg = tmp_path / "docs/operating_model/risk_register.md"
    risk_reg.write_text("# Risk Register\n## Risk\n## Impact\n## Mitigation")

    assert validate_operating_model(tmp_path) is True

    # Missing Header
    risk_reg.write_text("# Risk Register")
    assert validate_operating_model(tmp_path) is False
