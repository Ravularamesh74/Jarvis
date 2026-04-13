"""
Global constants for JARVIS system
"""

from pathlib import Path


# -----------------------------------
# APP INFO
# -----------------------------------

APP_NAME = "JARVIS"
APP_VERSION = "1.0.0"
ENV = "development"  # development | production


# -----------------------------------
# PATHS
# -----------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
MODEL_DIR = BASE_DIR / "models"

HISTORY_FILE = BASE_DIR / ".jarvis_history"

# Ensure directories exist
for path in [DATA_DIR, LOG_DIR, MODEL_DIR]:
    path.mkdir(parents=True, exist_ok=True)


# -----------------------------------
# MEMORY CONFIG
# -----------------------------------

SHORT_TERM_MAX_SIZE = 10

VECTOR_DIMENSION = 384
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

MEMORY_DB_PATH = DATA_DIR / "memory.db"


# -----------------------------------
# LLM CONFIG
# -----------------------------------

DEFAULT_MODEL = "gpt-4o-mini"   # change as needed
MAX_TOKENS = 2048
TEMPERATURE = 0.7
TOP_P = 0.9

STREAMING_ENABLED = True


# -----------------------------------
# AGENT CONFIG
# -----------------------------------

AGENT_TIMEOUT = 30  # seconds

AGENT_TYPES = [
    "planner",
    "coding",
    "automation",
    "research",
]


# -----------------------------------
# TOOL CONFIG
# -----------------------------------

TOOL_TIMEOUT = 10

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

ALLOWED_SHELL_COMMANDS = [
    "echo",
    "ls",
    "dir",
    "pwd",
    "whoami"
]


# -----------------------------------
# API CONFIG
# -----------------------------------

API_HOST = "0.0.0.0"
API_PORT = 8000

API_PREFIX = "/api"

REQUEST_TIMEOUT = 15


# -----------------------------------
# WEB CONFIG
# -----------------------------------

FRONTEND_URL = "http://localhost:3000"

CORS_ORIGINS = ["*"]  # restrict in production


# -----------------------------------
# VOICE CONFIG
# -----------------------------------

WAKE_WORD = "jarvis"

VOICE_ENABLED = True
CONTINUOUS_LISTENING = False

VOSK_MODEL_PATH = MODEL_DIR / "vosk"

TTS_RATE = 180


# -----------------------------------
# UI CONFIG
# -----------------------------------

THEME = "dark"

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600


# -----------------------------------
# LOGGING CONFIG
# -----------------------------------

LOG_LEVEL = "INFO"
LOG_FILE = LOG_DIR / "jarvis.log"


# -----------------------------------
# SECURITY
# -----------------------------------

ENABLE_AUTH = False

MAX_REQUEST_SIZE = 10_000  # characters

BLOCKED_KEYWORDS = [
    "rm -rf",
    "shutdown",
    "reboot",
]


# -----------------------------------
# EVENT TYPES (EVENT BUS)
# -----------------------------------

EVENT_USER_INPUT = "user_input"
EVENT_AI_RESPONSE = "ai_response"
EVENT_TOOL_USED = "tool_used"
EVENT_ERROR = "error"


# -----------------------------------
# CLI CONFIG
# -----------------------------------

CLI_PROMPT = "You: "
CLI_AI_PREFIX = "JARVIS: "

STREAM_DELAY = 0.01


# -----------------------------------
# DEBUG
# -----------------------------------

DEBUG_MODE = True
SHOW_TOOL_LOGS = True