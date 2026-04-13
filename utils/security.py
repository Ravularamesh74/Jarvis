"""
Advanced Security Module for JARVIS
Includes:
- JWT Authentication
- Encryption (Fernet AES)
- AST-based sandbox execution
"""

import re
import time
import ast
import jwt
import secrets
from typing import Dict, Any, Optional
from cryptography.fernet import Fernet

from utils.constants import MAX_REQUEST_SIZE


# -----------------------------------
# JWT CONFIG
# -----------------------------------

JWT_SECRET = "super_secret_key"  # move to .env later
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 3600  # seconds


# -----------------------------------
# JWT FUNCTIONS
# -----------------------------------

def create_jwt(payload: Dict[str, Any]) -> str:
    payload = payload.copy()
    payload["exp"] = int(time.time()) + JWT_EXPIRATION
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# -----------------------------------
# ENCRYPTION (FERNET AES)
# -----------------------------------

# Generate once and store securely!
FERNET_KEY = Fernet.generate_key()
cipher = Fernet(FERNET_KEY)


def encrypt_data(data: str) -> str:
    return cipher.encrypt(data.encode()).decode()


def decrypt_data(token: str) -> str:
    return cipher.decrypt(token.encode()).decode()


# -----------------------------------
# INPUT SANITIZATION
# -----------------------------------

def sanitize_input(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.strip()

    if len(text) > MAX_REQUEST_SIZE:
        raise ValueError("Input too large")

    return text.replace("\x00", "")


# -----------------------------------
# AST SANDBOX (CRITICAL)
# -----------------------------------

ALLOWED_NODES = {
    "Module", "Expr", "Assign", "Name", "Load",
    "BinOp", "Add", "Sub", "Mult", "Div",
    "Num", "Constant", "Call", "Compare",
    "Eq", "NotEq", "Lt", "Gt"
}


FORBIDDEN_FUNCTIONS = [
    "exec", "eval", "__import__", "open",
    "os", "sys", "subprocess"
]


def is_safe_ast(code: str) -> bool:
    """
    Parse and validate AST to prevent malicious execution
    """
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            node_name = type(node).__name__

            if node_name not in ALLOWED_NODES:
                return False

            # Block dangerous calls
            if isinstance(node, ast.Call):
                if hasattr(node.func, "id"):
                    if node.func.id in FORBIDDEN_FUNCTIONS:
                        return False

        return True

    except Exception:
        return False


# -----------------------------------
# SAFE EXECUTION (SANDBOX)
# -----------------------------------

SAFE_BUILTINS = {
    "print": print,
    "len": len,
    "range": range,
    "int": int,
    "float": float,
    "str": str,
    "sum": sum,
}


def safe_exec(code: str):
    """
    Execute code safely after AST validation
    """
    if not is_safe_ast(code):
        raise ValueError("Unsafe code detected")

    local_env = {}

    exec(code, {"__builtins__": SAFE_BUILTINS}, local_env)

    return local_env


# -----------------------------------
# API KEY GENERATION
# -----------------------------------

def generate_api_key() -> str:
    return f"jarvis_{secrets.token_hex(16)}"


# -----------------------------------
# RATE LIMIT (TOKEN BUCKET)
# -----------------------------------

_rate_store: Dict[str, list] = {}


def rate_limit(key: str, max_requests=10, window=60) -> bool:
    now = time.time()

    timestamps = _rate_store.get(key, [])
    timestamps = [t for t in timestamps if now - t < window]

    if len(timestamps) >= max_requests:
        return False

    timestamps.append(now)
    _rate_store[key] = timestamps
    return True


# -----------------------------------
# PERMISSIONS (RBAC)
# -----------------------------------

ROLES = ["admin", "user", "agent"]

PERMISSIONS = {
    "admin": ["*"],
    "user": ["chat"],
    "agent": ["chat", "tools"]
}


def has_permission(role: str, action: str) -> bool:
    allowed = PERMISSIONS.get(role, [])
    return "*" in allowed or action in allowed