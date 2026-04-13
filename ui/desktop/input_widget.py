from PyQt6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QTextEdit,
    QPushButton
)
from PyQt6.QtCore import pyqtSignal, Qt


class InputWidget(QWidget):
    """
    Advanced input widget for JARVIS UI.
    Supports multiline input, shortcuts, and async-safe state.
    """

    send_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        # Multi-line input
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Ask JARVIS...")
        self.input_field.setFixedHeight(60)

        # Buttons
        self.send_button = QPushButton("Send")
        self.voice_button = QPushButton("🎤")  # placeholder

        self.layout.addWidget(self.input_field)
        self.layout.addWidget(self.send_button)
        self.layout.addWidget(self.voice_button)

        self.setLayout(self.layout)

        # Connections
        self.send_button.clicked.connect(self.emit_text)

        # Override key press for Enter behavior
        self.input_field.keyPressEvent = self.handle_key_press

    # -----------------------------------
    # Input Handling
    # -----------------------------------

    def handle_key_press(self, event):
        """
        Enter = send
        Shift+Enter = newline
        """
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                # Allow newline
                QTextEdit.keyPressEvent(self.input_field, event)
            else:
                self.emit_text()
        else:
            QTextEdit.keyPressEvent(self.input_field, event)

    def emit_text(self):
        text = self.input_field.toPlainText().strip()

        if not text:
            return

        self.send_signal.emit(text)
        self.input_field.clear()

    # -----------------------------------
    # State Management (IMPORTANT)
    # -----------------------------------

    def set_loading(self, is_loading: bool):
        """
        Disable input while JARVIS is processing
        """
        self.input_field.setDisabled(is_loading)
        self.send_button.setDisabled(is_loading)

        if is_loading:
            self.send_button.setText("...")
        else:
            self.send_button.setText("Send")

    # -----------------------------------
    # Optional Voice Hook (Future)
    # -----------------------------------

    def enable_voice(self, callback):
        """
        Attach voice input handler
        """
        self.voice_button.clicked.connect(callback)