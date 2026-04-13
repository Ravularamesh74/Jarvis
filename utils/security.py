"""
Security utilities for JARVIS system
"""

import re
import secrets
import time
from typing import Dict, Any, Optional

from utils.constants import BLOCKED_KEYWORDS, MAX_REQUEST_SIZE


# -----------------------------------
# INPUT SANITIZATION
# -----------------------------------

def sanitize_input(text: str) -> str:
    """
    Remove dangerous patterns from input
    """
    if not isinstance(text, str):
        return ""

    text = text.strip()

    # Limit size
    if len(text) > MAX_REQUEST_SIZE:
        raise ValueError("Input too large")

    # Remove null bytes
    text = text.replace("\x00", "")

    return text


# -----------------------------------
# COMMAND FILTERING
# -----------------------------------

def is_safe_command(command: str) -> bool:
    """
    Check if command contains dangerous patterns
    """
    if not command:
        return False

    lowered = command.lower()

    for keyword in BLOCKED_KEYWORDS:
        if keyword in lowered:
            return False

    return True


# -----------------------------------
# CODE VALIDATION
# -----------------------------------

FORBIDDEN_PATTERNS = [
    r"import os",
    r"import sys",
    r"subprocess",
    r"eval\(",
    r"exec\(",
    r"open\(",
    r"__import__",
]

def is_safe_code(code: str) -> bool:
    """
    Basic static validation for unsafe code
    """
    code_lower = code.lower()

    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, code_lower):
            return False

    return True


# -----------------------------------
# TOKEN GENERATION
# -----------------------------------

def generate_token(length: int = 32) -> str:
    """
    Generate secure random token
    """
    return secrets.token_hex(length)


def generate_api_key() -> str:
    return f"jarvis_{generate_token(16)}"


# -----------------------------------
# PERMISSION CONTROL (RBAC BASIC)
# -----------------------------------

ROLES = ["admin", "user", "agent"]

PERMISSIONS = {
    "admin": ["*"],
    "user": ["chat", "basic_tools"],
    "agent": ["chat", "tools", "memory"]
}


def has_permission(role: str, action: str) -> bool:
    if role not in PERMISSIONS:
        return False

    allowed = PERMISSIONS[role]

    return "*" in allowed or action in allowed


# -----------------------------------
# RATE LIMITING (ADVANCED)
# -----------------------------------

_rate_limit_store: Dict[str, list] = {}


def rate_limit(
    key: str,
    max_requests: int = 5,
    window: int = 10
) -> bool:
    """
    Token bucket style limiter
    """
    now = time.time()

    requests = _rate_limit_store.get(key, [])

    # Remove old requests
    requests = [r for r in requests if now - r < window]

    if len(requests) >= max_requests:
        return False

    requests.append(now)
    _rate_limit_store[key] = requests

    return True


# -----------------------------------
# SAFE PAYLOAD VALIDATION
# -----------------------------------

def validate_payload(data: Dict[str, Any], required_fields: list):
    """
    Ensure required fields exist
    """
    if not isinstance(data, dict):
        raise ValueError("Invalid payload format")

    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing field: {field}")


# -----------------------------------
# PATH SAFETY
# -----------------------------------

def is_safe_path(base_path: str, target_path: str) -> bool:
    """
    Prevent directory traversal
    """
    import os

    base = os.path.abspath(base_path)
    target = os.path.abspath(os.path.join(base, target_path))

    return target.startswith(base)


# -----------------------------------
# SESSION MANAGEMENT (BASIC)
# -----------------------------------

_sessions: Dict[str, Dict[str, Any]] = {}


def create_session(user_id: str) -> str:
    token = generate_token(16)

    _sessions[token] = {
        "user_id": user_id,
        "created_at": time.time()
    }

    return token


def get_session(token: str) -> Optional[Dict[str, Any]]:
    return _sessions.get(token)


def delete_session(token: str):
    _sessions.pop(token, None)