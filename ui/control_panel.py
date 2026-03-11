from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QPushButton,
    QComboBox
)
from PySide6.QtCore import Signal
from ui.card import Card
from pygrabber.dshow_graph import FilterGraph


class ControlPanel(Card):

    start_clicked = Signal()
    stop_clicked = Signal()
    upload_clicked = Signal()
    camera_changed = Signal(int)
    ai_toggled = Signal(bool)
    clear_mission_clicked = Signal()

    plan_mission_clicked = Signal()
    upload_mission_clicked = Signal()

    def __init__(self):
        super().__init__()

        title = QLabel("Controls")
        title.setStyleSheet("color:white; font-weight:600;")

        start_btn = QPushButton("Start")
        start_btn.setStyleSheet("background:#22c55e; color:white;")
        start_btn.clicked.connect(self.start_clicked.emit)

        stop_btn = QPushButton("Stop")
        stop_btn.setStyleSheet("background:#ef4444; color:white;")
        stop_btn.clicked.connect(self.stop_clicked.emit)

        upload_btn = QPushButton("Upload Video")
        upload_btn.setStyleSheet("background:#2563eb; color:white;")
        upload_btn.clicked.connect(self.upload_clicked.emit)

        # Mission planning button
        plan_btn = QPushButton("Plan Mission")
        plan_btn.setStyleSheet("background:#f59e0b; color:white;")
        plan_btn.clicked.connect(self.plan_mission_clicked.emit)

        # Upload mission button
        upload_mission_btn = QPushButton("Upload Mission")
        upload_mission_btn.setStyleSheet("background:#dc2626; color:white;")
        upload_mission_btn.clicked.connect(self.upload_mission_clicked.emit)

        clear_mission_button = QPushButton("Clear Mission")
        clear_mission_button.setStyleSheet("background:#6b7280; color:white;")
        clear_mission_button.clicked.connect(self.clear_mission_clicked.emit)

        self.camera_select = QComboBox()
        self.camera_select.setMinimumWidth(250)
        self.camera_select.setStyleSheet("background:#2563eb; color:white;")

        self.populate_cameras()
        self.camera_select.currentIndexChanged.connect(self._emit_camera_change)

        layout = QHBoxLayout(self)
        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(self.camera_select)
        layout.addWidget(start_btn)
        layout.addWidget(stop_btn)
        layout.addWidget(upload_btn)
        layout.addWidget(plan_btn)
        layout.addWidget(upload_mission_btn)
        layout.addWidget(clear_mission_button)

    def populate_cameras(self):

        self.camera_select.clear()

        graph = FilterGraph()
        devices = graph.get_input_devices()

        if not devices:
            self.camera_select.addItem("No Camera Found", -1)
            return

        for index, name in enumerate(devices):
            self.camera_select.addItem(name, index)

        if len(devices) > 1:
            self.camera_select.setCurrentIndex(1)

    def _emit_camera_change(self, index):
        device_id = self.camera_select.itemData(index)
        if device_id is not None and device_id >= 0:
            self.camera_changed.emit(device_id)