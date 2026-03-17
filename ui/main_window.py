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
from ocr.osd_extractor import OCRWorker
from control.visioncontrol import VisionControl

class MainWindow(QMainWindow):

    def __init__(self,):
        super().__init__()
        self.worker = VideoWorker(device_id=1)

        self.resize(1700, 950)
        self.setWindowTitle("Main Window")

        central = QWidget()
        self.setCentralWidget(central)

        # self.status = StatusBar()
        self.video = VideoWidget()
        self.telemetry = TelemetryPanel()
        self.controls = ControlPanel()
        self.map_view = MapWidget()
        self.ocr = OCRWorker()
        self.visioncontrol = VisionControl()

        left = QVBoxLayout()
        left.addWidget(self.video, 6)
        left.addWidget(self.telemetry, 3)

        right = QVBoxLayout()
        right.addWidget(self.map_view, 1)   # full height now

        body = QHBoxLayout()
        body.addLayout(left, 3)
        body.addLayout(right, 2)

        layout = QVBoxLayout()

        # 🔼 Controls moved to TOP
        layout.addWidget(self.controls, 1)

        # Main content
        layout.addLayout(body, 9)

        # 🔽 Status moved to BOTTOM (optional)
        # layout.addWidget(self.status, 1)

        central.setLayout(layout)

        # VIDEO + TELEMETRY
        self.worker.frame_signal.connect(self.video.update_frame)
        self.worker.frame_signal.connect(self.ocr.receive_frame)
        self.worker.frame_signal.connect(self.visioncontrol.getFrame)
        self.video.clicked.connect(self.visioncontrol.selectedpoint)
        self.ocr.telemetry_signal.connect(self.telemetry.update)
        self.ocr.telemetry_signal.connect(self.map_view.update_position)

        # CONTROLS
        self.controls.start_clicked.connect(self.worker.start_stream)
        self.controls.start_clicked.connect(self.visioncontrol.start_control)
        self.controls.start_clicked.connect(self.ocr.start_ocr)
        self.controls.stop_clicked.connect(self.worker.stop_stream)
        self.controls.upload_clicked.connect(self.open_video_file)
        self.controls.camera_changed.connect(self.worker.change_camera)

        self.video.ai_toggled.connect(self.worker.enable_ai)

        # MISSION PLANNING
        self.controls.plan_mission_clicked.connect(self.map_view.enable_mission_planning)
        self.controls.upload_mission_clicked.connect(self.map_view.upload_mission)
        self.controls.clear_mission_clicked.connect(self.map_view.clear_mission)

        self.controls.clear_mission_clicked.connect(self.map_view.clear_mission)
        self.controls.clear_path_clicked.connect(self.map_view.clear_path)

    def closeEvent(self, event):
        self.worker.stop_stream()
        return super().closeEvent(event)


    def open_video_file(self):
        file_path, _ = QFileDialog.getOpenFileName( 
            self,
            "Select Video File",
            "",
            "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
 
        if file_path:
            self.worker.open_video_file(file_path)