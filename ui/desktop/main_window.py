from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from ui.desktop.chat_widget import ChatWidget
from ui.desktop.input_widget import InputWidget
from ui.desktop.status_bar import StatusBar


# -----------------------------------
# Worker (Prevents UI Freeze)
# -----------------------------------

class Worker(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, orchestrator, text: str):
        super().__init__()
        self.orchestrator = orchestrator
        self.text = text

    def run(self):
        try:
            result = self.orchestrator.handle(self.text)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))


# -----------------------------------
# Main Widget
# -----------------------------------

class MainWidget(QWidget):
    """
    Central UI controller for JARVIS desktop.
    Handles interaction between UI and backend.
    """

    def __init__(self, orchestrator):
        super().__init__()

        self.orchestrator = orchestrator

        # UI Components
        self.chat = ChatWidget()
        self.input = InputWidget()
        self.status = StatusBar()

        layout = QVBoxLayout()
        layout.addWidget(self.chat)
        layout.addWidget(self.input)
        layout.addWidget(self.status)

        self.setLayout(layout)

        # Connect input
        self.input.send_signal.connect(self.handle_input)

    # -----------------------------------
    # Input Handling
    # -----------------------------------

    def handle_input(self, text: str):
        self.chat.add_user_message(text)
        self.status.update_status("Thinking...")
        self.input.set_loading(True)

        # Run in background thread
        self.thread = QThread()
        self.worker = Worker(self.orchestrator, text)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_result)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.error.connect(self.thread.quit)

        self.thread.start()

    # -----------------------------------
    # Results Handling
    # -----------------------------------

    def on_result(self, result: str):
        self.chat.add_ai_message(result)
        self.status.update_status("Ready")
        self.input.set_loading(False)

    def on_error(self, error: str):
        self.chat.add_error_message(error)
        self.status.update_status("Error")
        self.input.set_loading(False)