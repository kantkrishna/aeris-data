# tests/unit/data-platform/test_secrets_manager.py
"""
Secrets Management Tests.

Validates US-19.1 for the SecretsManager interface and environment-based
provider, ensuring secrets are loaded securely or raise precise exceptions.
"""

import pytest
from src.security.secrets import EnvVarSecretsProvider
from src.exceptions.core import SecretNotFoundException


@pytest.fixture
def env_provider() -> EnvVarSecretsProvider:
    return EnvVarSecretsProvider()


def test_get_valid_secret(
    env_provider: EnvVarSecretsProvider, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given a set environment variable, get_secret returns its value."""
    monkeypatch.setenv("SNOWFLAKE_PASS", "SuperSecret123!")
    assert env_provider.get_secret("SNOWFLAKE_PASS") == "SuperSecret123!"


def test_missing_secret_raises_exception(env_provider: EnvVarSecretsProvider) -> None:
    """Given a missing secret, get_secret raises SecretNotFoundException."""
    with pytest.raises(SecretNotFoundException):
        env_provider.get_secret("NON_EXISTENT_SECRET")


def test_empty_secret_raises_exception(
    env_provider: EnvVarSecretsProvider, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Given an empty secret string, get_secret raises SecretNotFoundException."""
    monkeypatch.setenv("EMPTY_SECRET", "")
    with pytest.raises(SecretNotFoundException):
        env_provider.get_secret("EMPTY_SECRET")
