# tests/unit/data-platform/test_docs_linting.py
"""
Documentation and ADR Linting Tests.

This module validates that required Architectural Decision Records (ADRs),
capability matrices, and decision frameworks exist and conform to
required Markdown structures for Epics 13, 17, and 18.
"""

import os
import re


def test_capability_matrix_format() -> None:
    """Validates US-13.1 capability matrix exists with required columns."""
    filepath = "docs/architecture/engine_capability_matrix.md"
    assert os.path.exists(filepath), f"Matrix document missing at {filepath}"

    with open(filepath, "r") as f:
        content = f.read()

    assert "Capability" in content
    assert "Snowflake Support" in content
    assert "Databricks Support" in content


def test_workload_framework_format() -> None:
    """Validates US-17.1 placement framework contains required scoring dimensions."""
    filepath = "docs/architecture/workload_placement_framework.md"
    assert os.path.exists(filepath), f"Framework missing at {filepath}"

    with open(filepath, "r") as f:
        content = f.read()

    expected_sections = [
        "Characteristics",
        "Performance",
        "Cost",
        "Ecosystem Requirements",
    ]
    for section in expected_sections:
        assert section in content, f"Missing section '{section}' in framework."


def test_multi_engine_adr_format() -> None:
    """Validates US-18.1 multi-engine ADR follows standard headers."""
    filepath = "docs/adr/004_multi_engine_interoperability.md"
    assert os.path.exists(filepath), f"ADR missing at {filepath}"

    with open(filepath, "r") as f:
        content = f.read()

    headers = ["Context", "Decision", "Consequences", "Status"]
    for header in headers:
        assert re.search(r"#+\s+" + header, content), f"ADR missing header: {header}"

    assert "Accepted" in content or "Proposed" in content, "Invalid ADR status"
