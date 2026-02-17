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
from video.video_worker import VideoWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(1700, 950)
        self.setWindowTitle("Drone GCS")

        # ---- Central widget ----
        central = QWidget()
        self.setCentralWidget(central)

        # ---- UI components (CREATE FIRST) ----
        self.status = StatusBar()
        self.video = VideoWidget()
        self.telemetry = TelemetryPanel()
        self.controls = ControlPanel()
        self.map_view = MapWidget()

        # ---- Layouts ----
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

        # ---- Worker ----
        self.worker = VideoWorker(device_id=0)

        # ---- Signals ----
        self.worker.frame_signal.connect(self.video.update_frame)
        self.worker.telemetry_signal.connect(self.telemetry.update)
        self.worker.telemetry_signal.connect(self.map_view.update_position)

        self.video.ai_toggled.connect(self.worker.enable_ai)
        self.controls.upload_clicked.connect(self.open_video_file)
        self.controls.camera_select.currentIndexChanged.connect(self.switch_camera)

        self.worker.start()

    def open_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )

        if file_path:
            print(f"[INFO] Loading video: {file_path}")
            self.worker.open_video_file(file_path)

    def switch_camera(self, index):
        """Switch to a different camera device"""
        self.worker.change_camera(index)
