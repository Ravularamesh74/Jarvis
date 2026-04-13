from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextBrowser,
    QPushButton,
    QHBoxLayout
)
from PyQt6.QtCore import Qt


class ChatWidget(QWidget):
    """
    Advanced chat display widget for JARVIS UI.
    Supports formatted messages, streaming, and controls.
    """

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        # Chat display
        self.chat_area = QTextBrowser()
        self.chat_area.setOpenExternalLinks(True)

        # Controls
        self.clear_btn = QPushButton("Clear")
        self.copy_btn = QPushButton("Copy All")

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.clear_btn)
        controls_layout.addWidget(self.copy_btn)
        controls_layout.addStretch()

        self.layout.addWidget(self.chat_area)
        self.layout.addLayout(controls_layout)

        self.setLayout(self.layout)

        # Internal state
        self._stream_buffer = ""

        # Connect buttons
        self.clear_btn.clicked.connect(self.clear)
        self.copy_btn.clicked.connect(self.copy_all)

    # -----------------------------------
    # Message Rendering
    # -----------------------------------

    def add_user_message(self, text: str):
        self._append_message("You", text, "#4FC3F7")

    def add_ai_message(self, text: str):
        self._append_message("JARVIS", text, "#81C784")

    def add_system_message(self, text: str):
        self._append_message("System", text, "#FFD54F")

    def add_error_message(self, text: str):
        self._append_message("Error", text, "#E57373")

    def _append_message(self, sender: str, text: str, color: str):
        html = f"""
        <div style="
            margin:8px;
            padding:10px;
            border-radius:8px;
            background-color:#1e1e1e;
        ">
            <b style="color:{color};">{sender}:</b><br>
            <span style="color:#e0e0e0;">{text}</span>
        </div>
        """

        self.chat_area.append(html)
        self._auto_scroll()

    # -----------------------------------
    # Streaming Support (IMPORTANT)
    # -----------------------------------

    def start_stream(self):
        """
        Begin streaming response (AI typing effect)
        """
        self._stream_buffer = ""
        self.chat_area.append(
            '<div style="margin:8px; padding:10px; background:#1e1e1e;">'
            '<b style="color:#81C784;">JARVIS:</b><br>'
            '<span id="stream"></span></div>'
        )

    def stream_chunk(self, chunk: str):
        """
        Append chunk of streaming text
        """
        self._stream_buffer += chunk
        self._update_stream()

    def end_stream(self):
        """
        Finalize stream
        """
        self._stream_buffer = ""

    def _update_stream(self):
        cursor = self.chat_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)

        # Simple append (QTextBrowser doesn’t support DOM updates easily)
        self.chat_area.append(
            f'<span style="color:#e0e0e0;">{self._stream_buffer}</span>'
        )

        self._auto_scroll()

    # -----------------------------------
    # Utilities
    # -----------------------------------

    def clear(self):
        self.chat_area.clear()

    def copy_all(self):
        text = self.chat_area.toPlainText()
        QApplication.clipboard().setText(text)

    def _auto_scroll(self):
        self.chat_area.verticalScrollBar().setValue(
            self.chat_area.verticalScrollBar().maximum()
        )