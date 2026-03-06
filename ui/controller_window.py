from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFileDialog
)
from PySide6.QtCore import Signal
from PySide6.QtGui import QImage, QPixmap
from ui.card import Card
import cv2


class ControllerToggleButton(QPushButton):
    """Toggle button for drone controller, styled like the AI mode toggle."""
    toggled_signal = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_checked = False
        self.setCheckable(True)
        self.setMinimumHeight(36)
        self.setMaximumWidth(160)
        self.clicked.connect(self._on_clicked)
        self._update_style()

    def _on_clicked(self):
        self._is_checked = not self._is_checked
        self._update_style()
        self.toggled_signal.emit(self._is_checked)

    def _update_style(self):
        if self._is_checked:
            self.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border-radius: 6px;
                    background: #3b82f6;
                    color: white;
                    font-weight: 600;
                    border: 2px solid #2563eb;
                }
                QPushButton:hover { background: #2563eb; }
                QPushButton:pressed { background: #1d4ed8; }
            """)
            self.setText("Controller: ON")
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
                QPushButton:hover { background: #c4c7ce; }
                QPushButton:pressed { background: #b4b8c0; }
            """)
            self.setText("Controller: OFF")


class PlainVideoWindow(QMainWindow):
    """Window 1: Plain video feed (no AI) with drone controller toggle."""

    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.setWindowTitle("Controller Window")
        self.resize(1000, 700)

        central = QWidget()
        self.setCentralWidget(central)

        # Video display
        self.video_label = QLabel()
        self.video_label.setStyleSheet("background: black; border-radius: 10px;")
        self.video_label.setScaledContents(True)

        # Controller toggle
        self.ctrl_toggle = ControllerToggleButton()
        self.ctrl_toggle.toggled_signal.connect(self._toggle_controller)

        # Top bar
        top_bar = QHBoxLayout()
        title = QLabel("Live Feed")
        title.setStyleSheet("color: #1f2937; font-weight: 700; font-size: 16px;")
        top_bar.addWidget(title)
        top_bar.addStretch()
        top_bar.addWidget(self.ctrl_toggle)

        # Control buttons
        controls_bar = QHBoxLayout()

        self.camera_select = QComboBox()
        self.camera_select.setMinimumWidth(250)
        self.camera_select.setStyleSheet("background:#2563eb; color:white;")
        self._populate_cameras()
        self.camera_select.currentIndexChanged.connect(self._on_camera_change)

        start_btn = QPushButton("Start")
        start_btn.setStyleSheet("background:#22c55e; color:white; padding: 8px 16px; border-radius: 6px;")
        start_btn.clicked.connect(self.worker.start_stream)

        stop_btn = QPushButton("Stop")
        stop_btn.setStyleSheet("background:#ef4444; color:white; padding: 8px 16px; border-radius: 6px;")
        stop_btn.clicked.connect(self.worker.stop_stream)

        upload_btn = QPushButton("Upload Video")
        upload_btn.setStyleSheet("background:#2563eb; color:white; padding: 8px 16px; border-radius: 6px;")
        upload_btn.clicked.connect(self._open_video_file)

        controls_bar.addWidget(self.camera_select)
        controls_bar.addStretch()
        controls_bar.addWidget(start_btn)
        controls_bar.addWidget(stop_btn)
        controls_bar.addWidget(upload_btn)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        layout.addLayout(top_bar)
        layout.addWidget(self.video_label, 1)
        layout.addLayout(controls_bar)

        # Connect raw frame signal
        self.worker.raw_frame_signal.connect(self.update_frame)

    def update_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(img))

    def _toggle_controller(self, on):
        # Controller will be implemented later
        print(f"[INFO] Controller toggled: {'ON' if on else 'OFF'}")

    def _populate_cameras(self):
        self.camera_select.clear()
        try:
            from pygrabber.dshow_graph import FilterGraph
            graph = FilterGraph()
            devices = graph.get_input_devices()
            if not devices:
                self.camera_select.addItem("No Camera Found", -1)
                return
            for index, name in enumerate(devices):
                self.camera_select.addItem(name, index)
            if len(devices) > 1:
                self.camera_select.setCurrentIndex(1)
        except Exception:
            self.camera_select.addItem("No Camera Found", -1)

    def _on_camera_change(self, index):
        device_id = self.camera_select.itemData(index)
        if device_id is not None and device_id >= 0:
            self.worker.change_camera(device_id)

    def _open_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Video File", "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if file_path:
            self.worker.open_video_file(file_path)

    def closeEvent(self, event):
        event.accept()
