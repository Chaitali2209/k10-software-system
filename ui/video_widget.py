from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtCore import Signal
from ui.card import Card
from PySide6.QtGui import QImage, QPixmap
import cv2

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

class VideoWidget(Card):
    ai_toggled = Signal(bool)
    
    def __init__(self):
        super().__init__()
        self.label = QLabel()
        self.label.setStyleSheet("background:black; border-radius:10px;")
        self.label.setScaledContents(True)

        self.ai_toggle = ToggleButton("AI Mode")
        self.ai_toggle.toggled_signal.connect(self.ai_toggled.emit)

        # Top bar with toggle button in top right
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.ai_toggle)
        top_bar.setContentsMargins(8, 0, 8, 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addLayout(top_bar)
        layout.addWidget(self.label)

    def update_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(img))
