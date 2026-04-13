from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import QTimer, Qt
from datetime import datetime


class StatusBar(QWidget):
    """
    Advanced status bar for JARVIS UI.
    Shows system state, activity indicator, and progress.
    """

    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Timestamp
        self.time_label = QLabel(self._current_time())
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # Activity spinner (text-based)
        self.spinner_label = QLabel("")
        self.spinner_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.spinner_index = 0

        self.timer = QTimer()
        self.timer.timeout.connect(self._update_spinner)

        # Progress bar (hidden by default)
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximumWidth(150)

        # Layout
        self.layout.addWidget(self.status_label)
        self.layout.addWidget(self.spinner_label)
        self.layout.addWidget(self.progress)
        self.layout.addStretch()
        self.layout.addWidget(self.time_label)

        self.setLayout(self.layout)

        # Time updater
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self._update_time)
        self.clock_timer.start(1000)

    # -----------------------------------
    # Status Updates
    # -----------------------------------

    def update_status(self, text: str, state: str = "normal"):
        """
        Update status with optional state:
        normal | thinking | error | success
        """
        self.status_label.setText(f"{text}")

        if state == "thinking":
            self._start_spinner()
            self.status_label.setStyleSheet("color: #FFD54F;")  # yellow

        elif state == "error":
            self._stop_spinner()
            self.status_label.setStyleSheet("color: #E57373;")  # red

        elif state == "success":
            self._stop_spinner()
            self.status_label.setStyleSheet("color: #81C784;")  # green

        else:
            self._stop_spinner()
            self.status_label.setStyleSheet("color: #E0E0E0;")  # default

    # -----------------------------------
    # Spinner Logic
    # -----------------------------------

    def _start_spinner(self):
        if not self.timer.isActive():
            self.timer.start(100)

    def _stop_spinner(self):
        self.timer.stop()
        self.spinner_label.setText("")

    def _update_spinner(self):
        self.spinner_label.setText(self.spinner_frames[self.spinner_index])
        self.spinner_index = (self.spinner_index + 1) % len(self.spinner_frames)

    # -----------------------------------
    # Progress Control
    # -----------------------------------

    def show_progress(self, value: int = 0):
        self.progress.setVisible(True)
        self.progress.setValue(value)

    def update_progress(self, value: int):
        self.progress.setValue(value)

    def hide_progress(self):
        self.progress.setVisible(False)

    # -----------------------------------
    # Time Handling
    # -----------------------------------

    def _current_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def _update_time(self):
        self.time_label.setText(self._current_time())