# src/observability/logging.py
"""
Observability Logging Utilities.

Implements US-19.2. Handles pre-processing of log streams to scrub 
dynamically injected credentials and tokens before persistence.
"""
import re

def mask_secrets(log_message: str) -> str:
    """Regex based masking replacing password portions in connection URLs with ***."""
    # Matches patterns like scheme://user:password@host by ensuring no slashes or spaces exist 
    # between the colon and the @ symbol.
    masked_message = re.sub(r'([a-zA-Z0-9_-]+):([^@\s/]+)@', r'\1:***@', log_message)
    return masked_message