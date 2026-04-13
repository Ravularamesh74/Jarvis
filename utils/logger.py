"""
Central logging system for JARVIS
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import sys

from utils.constants import LOG_DIR, LOG_LEVEL, LOG_FILE


# -----------------------------------
# COLOR SUPPORT (OPTIONAL)
# -----------------------------------

class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",   # Blue
        "INFO": "\033[92m",    # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "CRITICAL": "\033[95m"
    }
    RESET = "\033[0m"

    def format(self, record):
        color = self.COLORS.get(record.levelname, "")
        message = super().format(record)
        return f"{color}{message}{self.RESET}"


# -----------------------------------
# LOGGER SETUP
# -----------------------------------

def setup_logger(name: str = "jarvis") -> logging.Logger:
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger  # prevent duplicate handlers

    logger.setLevel(LOG_LEVEL)

    # Ensure log directory exists
    Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

    # -----------------------------------
    # FORMAT
    # -----------------------------------

    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # -----------------------------------
    # FILE HANDLER (ROTATING)
    # -----------------------------------

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(logging.Formatter(log_format))

    # -----------------------------------
    # CONSOLE HANDLER (COLORED)
    # -----------------------------------

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColorFormatter(log_format))

    # -----------------------------------
    # ADD HANDLERS
    # -----------------------------------

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# -----------------------------------
# GLOBAL LOGGER
# -----------------------------------

logger = setup_logger()


# -----------------------------------
# HELPER FUNCTIONS
# -----------------------------------

def get_logger(name: str) -> logging.Logger:
    return setup_logger(name)


def log_exception(logger: logging.Logger, e: Exception):
    logger.error(f"Exception: {str(e)}", exc_info=True)