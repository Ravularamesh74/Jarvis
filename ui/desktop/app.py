import sys
import logging
import traceback
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox

# UI
from ui.desktop.main_window import MainWindow
from ui.desktop.styles import DARK_STYLE

# Core (connect your backend)
from core.orchestrator import Orchestrator
from memory.memory_manager import MemoryManager
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.vector_store import VectorStore


# -----------------------------------
# Logging Setup
# -----------------------------------

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "jarvis.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )


# -----------------------------------
# Global Exception Handler
# -----------------------------------

def handle_exception(exc_type, exc_value, exc_traceback):
    error_msg = "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )

    logging.error("Unhandled Exception:\n%s", error_msg)

    # Show popup (prevents silent crash)
    QMessageBox.critical(
        None,
        "JARVIS Error",
        f"An unexpected error occurred:\n{exc_value}",
    )


# -----------------------------------
# Build Core System
# -----------------------------------

def build_system():
    short_term = ShortTermMemory(max_size=10)
    long_term = LongTermMemory(db=None)  # plug your DB here
    vector_store = VectorStore()

    memory_manager = MemoryManager(
        short_term=short_term,
        long_term=long_term,
        vector_store=vector_store,
    )

    from core.registry import CentralRegistry
    registry = CentralRegistry(brain=None, memory=memory_manager, context=None)

    orchestrator = Orchestrator(memory=memory_manager, registry=registry)

    return orchestrator


# -----------------------------------
# Main App Runner
# -----------------------------------

def run_app():
    setup_logging()

    # Catch all unhandled exceptions
    sys.excepthook = handle_exception

    app = QApplication(sys.argv)

    # Apply styling
    app.setStyleSheet(DARK_STYLE)

    # Build backend system
    orchestrator = build_system()

    # Create main window
    window = MainWindow(orchestrator=orchestrator)
    window.show()

    logging.info("JARVIS UI started")

    try:
        exit_code = app.exec()
        logging.info("JARVIS UI closed")
        sys.exit(exit_code)

    except Exception as e:
        logging.error("Fatal error: %s", str(e))
        sys.exit(1)


# -----------------------------------
# Entry Point
# -----------------------------------

if __name__ == "__main__":
    run_app()