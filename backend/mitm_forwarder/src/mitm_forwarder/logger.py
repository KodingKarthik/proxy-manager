"""Logging setup with token masking."""

import logging
import re
from typing import Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def mask_token(token: str) -> str:
    """
    Mask authorization token for logging.
    
    Args:
        token: Token string to mask
        
    Returns:
        Masked token (shows first 8 chars and last 4 chars)
    """
    if not token or len(token) <= 12:
        return "***"
    return f"{token[:8]}...{token[-4:]}"


def mask_authorization_header(value: str) -> str:
    """
    Mask Authorization header value in logs.
    
    Args:
        value: Authorization header value (e.g., "Bearer token123")
        
    Returns:
        Masked value
    """
    if not value:
        return value
    
    # Match "Bearer <token>" or "Basic <token>"
    match = re.match(r"^(Bearer|Basic)\s+(.+)$", value, re.IGNORECASE)
    if match:
        auth_type = match.group(1)
        token = match.group(2)
        return f"{auth_type} {mask_token(token)}"
    
    return "***"


def safe_log_dict(data: dict[str, Any]) -> dict[str, Any]:
    """
    Create a safe version of dict for logging (masks sensitive fields).
    
    Args:
        data: Dictionary to sanitize
        
    Returns:
        Sanitized dictionary
    """
    safe = data.copy()
    
    # Mask common sensitive fields
    sensitive_keys = ["authorization", "x-client-authorization", "token", "password", "api_key"]
    
    for key in safe.keys():
        if any(sensitive in key.lower() for sensitive in sensitive_keys):
            if isinstance(safe[key], str):
                safe[key] = mask_authorization_header(safe[key])
            else:
                safe[key] = "***"
    
    return safe

