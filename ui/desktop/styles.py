# -----------------------------------
# JARVIS DARK THEME (Production UI)
# -----------------------------------

DARK_STYLE = """
/* -----------------------------------
   GLOBAL
----------------------------------- */
QWidget {
    background-color: #121212;
    color: #E0E0E0;
    font-family: "Segoe UI", "Roboto", sans-serif;
    font-size: 14px;
}

/* -----------------------------------
   TEXT DISPLAY (CHAT)
----------------------------------- */
QTextBrowser {
    background-color: #181818;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 10px;
}

/* Scrollbar */
QScrollBar:vertical {
    background: #121212;
    width: 10px;
    margin: 2px;
}

QScrollBar::handle:vertical {
    background: #2A2A2A;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #3A3A3A;
}

/* -----------------------------------
   INPUT FIELD
----------------------------------- */
QTextEdit {
    background-color: #1E1E1E;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 8px;
    selection-background-color: #1f6feb;
}

/* -----------------------------------
   BUTTONS
----------------------------------- */
QPushButton {
    background-color: #1f6feb;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #388bfd;
}

QPushButton:pressed {
    background-color: #1a5fd0;
}

QPushButton:disabled {
    background-color: #444;
    color: #999;
}

/* -----------------------------------
   STATUS BAR
----------------------------------- */
QLabel {
    font-size: 13px;
}

/* -----------------------------------
   PROGRESS BAR
----------------------------------- */
QProgressBar {
    background-color: #1E1E1E;
    border: 1px solid #2A2A2A;
    border-radius: 5px;
    text-align: center;
}

QProgressBar::chunk {
    background-color: #1f6feb;
    border-radius: 5px;
}

/* -----------------------------------
   TOOLTIP
----------------------------------- */
QToolTip {
    background-color: #1E1E1E;
    color: #E0E0E0;
    border: 1px solid #2A2A2A;
    padding: 5px;
}

/* -----------------------------------
   SELECTION + FOCUS
----------------------------------- */
*:focus {
    outline: none;
    border: 1px solid #1f6feb;
}
"""