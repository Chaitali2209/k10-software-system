from PySide6.QtWidgets import QLabel, QHBoxLayout, QPushButton, QCheckBox
from PySide6.QtCore import Signal, Qt
from ui.card import Card


class ToggleButton(QPushButton):
    """Custom toggle button with proper visual feedback"""
    toggled_signal = Signal(bool)
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._is_checked = False
        self.setCheckable(True)
        self.setMinimumHeight(36)
        self.setMaximumWidth(120)
        self.clicked.connect(self._on_clicked)
        self._update_style()
    
    def _on_clicked(self):
        """Handle toggle click"""
        self._is_checked = not self._is_checked
        self._update_style()
        self.toggled_signal.emit(self._is_checked)
    
    def _update_style(self):
        """Update button style based on state"""
        if self._is_checked:
            self.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 6px;
                    background: #22c55e;
                    color: white;
                    font-weight: 600;
                    border: 2px solid #16a34a;
                }
                QPushButton:hover {
                    background: #16a34a;
                }
                QPushButton:pressed {
                    background: #15803d;
                }
            """)
            self.setText("AI Mode: ON")
        else:
            self.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 6px;
                    background: #d1d5db;
                    color: #374151;
                    font-weight: 600;
                    border: 2px solid #9ca3af;
                }
                QPushButton:hover {
                    background: #c4c7ce;
                }
                QPushButton:pressed {
                    background: #b4b8c0;
                }
            """)
            self.setText("AI Mode: OFF")
    
    def is_checked(self):
        """Get current toggle state"""
        return self._is_checked
    
    def set_checked(self, checked):
        """Set toggle state"""
        self._is_checked = checked
        self._update_style()


class ControlPanel(Card):
    ai_toggled = Signal(bool)
    upload_clicked = Signal()

    def __init__(self):
        super().__init__()

        title = QLabel("Controls")
        title.setStyleSheet("font-weight:600; font-size:14px;")

        upload_btn = QPushButton("Upload Video")
        upload_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border-radius: 6px;
                background: #2563eb;
                color: white;
            }
        """)
        upload_btn.clicked.connect(self.upload_clicked.emit)

        ai_toggle = ToggleButton("AI Mode")
        ai_toggle.toggled_signal.connect(self.ai_toggled.emit)

        layout = QHBoxLayout(self)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(upload_btn)
        layout.addWidget(ai_toggle)
