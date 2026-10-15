# src/security/secrets.py
"""
Secrets Management Abstraction.

Implements US-19.1. Provides abstract decoupling for credential retrieval,
defaulting to Environment Variables (via .env files) for initial deployments, 
but extensible to Azure Key Vault / AWS Secrets Manager.
"""
import os
from dotenv import load_dotenv
from abc import ABC, abstractmethod
from src.exceptions.core import SecretNotFoundException

# Load environment variables from a local .env file if present
load_dotenv()

class SecretsManager(ABC):
    @abstractmethod
    def get_secret(self, key: str) -> str:
        """Retrieves a secret securely."""
        pass

class EnvVarSecretsProvider(SecretsManager):
    def get_secret(self, key: str) -> str:
        secret = os.environ.get(key)
        if not secret or secret.strip() == "":
            raise SecretNotFoundException(f"Secret '{key}' not found or is empty.")
        return secret