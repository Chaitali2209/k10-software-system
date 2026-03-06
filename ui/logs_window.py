import sys
import logging
from datetime import datetime

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QFrame
)
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QFont, QTextCursor, QColor


class LogStream(QObject):
    """Redirect stdout/stderr to a Qt signal for display in the logs window."""
    text_written = Signal(str)

    def __init__(self, original_stream=None):
        super().__init__()
        self.original_stream = original_stream

    def write(self, text):
        if text.strip():
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            formatted = f"[{timestamp}] {text.rstrip()}"
            self.text_written.emit(formatted)
        # Also print to original stream (for debugging)
        if self.original_stream:
            self.original_stream.write(text)
            self.original_stream.flush()

    def flush(self):
        if self.original_stream:
            self.original_stream.flush()


class LogsWindow(QMainWindow):
    """Window 3: Technical logs display."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Logs window")
        self.resize(800, 600)

        central = QWidget()
        self.setCentralWidget(central)

        # Title bar
        title = QLabel("Technical Logs")
        title.setFont(QFont("Inter", 16, QFont.Bold))
        title.setStyleSheet("color: #1f2937; margin: 4px;")

        # Control buttons
        clear_btn = QPushButton("Clear")
        clear_btn.setStyleSheet(
            "background: #ef4444; color: white; padding: 6px 16px; "
            "border-radius: 6px; font-weight: 600;"
        )
        clear_btn.clicked.connect(self._clear_logs)

        self.auto_scroll_btn = QPushButton("Auto-Scroll: ON")
        self.auto_scroll_btn.setCheckable(True)
        self.auto_scroll_btn.setChecked(True)
        self._auto_scroll = True
        self.auto_scroll_btn.setStyleSheet(
            "background: #22c55e; color: white; padding: 6px 16px; "
            "border-radius: 6px; font-weight: 600;"
        )
        self.auto_scroll_btn.clicked.connect(self._toggle_auto_scroll)

        top_bar = QHBoxLayout()
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.auto_scroll_btn)
        top_bar.addWidget(clear_btn)

        # Log display
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 11))
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #0d1117;
                color: #c9d1d9;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 10px;
            }
        """)

        # Stats bar
        self.stats_label = QLabel("Lines: 0")
        self.stats_label.setStyleSheet("color: #6b7280; font-size: 12px;")

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addLayout(top_bar)
        layout.addWidget(self.log_display, 1)
        layout.addWidget(self.stats_label)

        # Set up log capturing
        self._line_count = 0
        self._setup_log_capture()

        # Initial startup log
        self.append_log("[SYSTEM] Logs window initialized")
        self.append_log("[SYSTEM] Application started")

    def _setup_log_capture(self):
        """Redirect stdout and stderr to the log display."""
        self.stdout_stream = LogStream(sys.stdout)
        self.stderr_stream = LogStream(sys.stderr)
        self.stdout_stream.text_written.connect(self._on_stdout)
        self.stderr_stream.text_written.connect(self._on_stderr)
        sys.stdout = self.stdout_stream
        sys.stderr = self.stderr_stream

    def _on_stdout(self, text):
        self._append_colored(text, "#c9d1d9")

    def _on_stderr(self, text):
        self._append_colored(text, "#f87171")

    def _append_colored(self, text, color):
        self._line_count += 1

        # Color-code based on content
        if "[ERROR]" in text or "[YOLO ERROR]" in text or "[OCR ERROR]" in text:
            color = "#f87171"  # red
        elif "[WARN]" in text:
            color = "#fbbf24"  # yellow
        elif "[INFO]" in text:
            color = "#60a5fa"  # blue
        elif "[SYSTEM]" in text:
            color = "#34d399"  # green

        cursor = self.log_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertHtml(f'<span style="color:{color};">{text}</span><br>')

        if self._auto_scroll:
            self.log_display.setTextCursor(cursor)
            self.log_display.ensureCursorVisible()

        self.stats_label.setText(f"Lines: {self._line_count}")

    def append_log(self, text):
        """Programmatically add a log entry."""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        formatted = f"[{timestamp}] {text}"
        self._append_colored(formatted, "#c9d1d9")

    def _clear_logs(self):
        self.log_display.clear()
        self._line_count = 0
        self.stats_label.setText("Lines: 0")

    def _toggle_auto_scroll(self):
        self._auto_scroll = not self._auto_scroll
        if self._auto_scroll:
            self.auto_scroll_btn.setText("Auto-Scroll: ON")
            self.auto_scroll_btn.setStyleSheet(
                "background: #22c55e; color: white; padding: 6px 16px; "
                "border-radius: 6px; font-weight: 600;"
            )
        else:
            self.auto_scroll_btn.setText("Auto-Scroll: OFF")
            self.auto_scroll_btn.setStyleSheet(
                "background: #d1d5db; color: #374151; padding: 6px 16px; "
                "border-radius: 6px; font-weight: 600;"
            )

    def closeEvent(self, event):
        """Restore original streams on close."""
        sys.stdout = self.stdout_stream.original_stream
        sys.stderr = self.stderr_stream.original_stream
        event.accept()
