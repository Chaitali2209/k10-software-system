from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog
)

from ui.video_widget import VideoWidget
from ui.telemetry_panel import TelemetryPanel
from ui.control_panel import ControlPanel
from ui.map_widget import MapWidget
from ui.status_bar import StatusBar


class MainWindow(QMainWindow):
    """Window 2: AI Inference video feed with telemetry and map."""

    def __init__(self, worker):
        super().__init__()
        self.worker = worker

        self.resize(1700, 950)
        self.setWindowTitle("Main Window")

        central = QWidget()
        self.setCentralWidget(central)

        self.status = StatusBar()
        self.video = VideoWidget()
        self.telemetry = TelemetryPanel()
        self.controls = ControlPanel()
        self.map_view = MapWidget()

        left = QVBoxLayout()
        left.addWidget(self.video, 6)
        left.addWidget(self.telemetry, 3)

        right = QVBoxLayout()
        right.addWidget(self.map_view, 7)
        right.addWidget(self.controls, 1)

        body = QHBoxLayout()
        body.addLayout(left, 3)
        body.addLayout(right, 2)

        layout = QVBoxLayout()
        layout.addWidget(self.status, 1)
        layout.addLayout(body, 9)

        central.setLayout(layout)

        # ---- SIGNALS ----
        self.worker.frame_signal.connect(self.video.update_frame)
        self.worker.telemetry_signal.connect(self.telemetry.update)
        self.worker.telemetry_signal.connect(self.map_view.update_position)

        self.controls.start_clicked.connect(self.worker.start_stream)
        self.controls.stop_clicked.connect(self.worker.stop_stream)
        self.controls.upload_clicked.connect(self.open_video_file)
        self.controls.camera_changed.connect(self.worker.change_camera)
        self.video.ai_toggled.connect(self.worker.enable_ai)

    def open_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )

        if file_path:
            self.worker.open_video_file(file_path)
