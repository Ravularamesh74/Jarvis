"""
Utility helper functions for JARVIS system
"""

import time
import hashlib
import logging
from typing import Any, Dict, Optional
from datetime import datetime
from functools import wraps

from utils.constants import LOG_LEVEL


# -----------------------------------
# LOGGING
# -----------------------------------

logger = logging.getLogger("jarvis.helpers")
logger.setLevel(LOG_LEVEL)


# -----------------------------------
# TIME UTILITIES
# -----------------------------------

def current_timestamp() -> float:
    return time.time()


def current_datetime() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def measure_time(func):
    """
    Decorator to measure execution time
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        logger.info(f"{func.__name__} executed in {end - start:.4f}s")
        return result

    return wrapper


# -----------------------------------
# STRING UTILITIES
# -----------------------------------

def clean_text(text: str) -> str:
    return text.strip()


def truncate_text(text: str, max_length: int = 200) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def safe_lower(text: Optional[str]) -> str:
    return text.lower() if text else ""


# -----------------------------------
# HASHING / IDs
# -----------------------------------

def generate_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def generate_id(prefix: str = "") -> str:
    return f"{prefix}_{int(time.time() * 1000)}"


# -----------------------------------
# DICT UTILITIES
# -----------------------------------

def safe_get(data: Dict, key: str, default=None):
    return data.get(key, default)


def deep_get(data: Dict, keys: list, default=None):
    """
    Access nested dictionary safely
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return default
    return data if data is not None else default


# -----------------------------------
# RETRY LOGIC
# -----------------------------------

def retry(func, retries=3, delay=1):
    """
    Retry decorator for unstable operations
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        for attempt in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.warning(f"Retry {attempt+1}/{retries} failed: {str(e)}")
                time.sleep(delay)

        raise Exception(f"{func.__name__} failed after {retries} retries")

    return wrapper


# -----------------------------------
# VALIDATION
# -----------------------------------

def is_valid_string(text: Any) -> bool:
    return isinstance(text, str) and bool(text.strip())


def is_valid_dict(data: Any) -> bool:
    return isinstance(data, dict)


# -----------------------------------
# SAFE EXECUTION
# -----------------------------------

def safe_execute(func, *args, default=None, **kwargs):
    """
    Executes function safely without crashing system
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Safe execution failed: {str(e)}")
        return default


# -----------------------------------
# FORMATTERS
# -----------------------------------

def format_response(
    success: bool,
    result: Any = None,
    error: Optional[str] = None
) -> Dict[str, Any]:
    return {
        "success": success,
        "result": result,
        "error": error,
        "timestamp": current_datetime()
    }


# -----------------------------------
# RATE LIMIT (SIMPLE)
# -----------------------------------

_last_called = {}

def rate_limit(key: str, cooldown: float = 1.0) -> bool:
    """
    Prevent spamming (returns True if allowed)
    """
    now = time.time()

    if key in _last_called:
        if now - _last_called[key] < cooldown:
            return False

    _last_called[key] = now
    return True