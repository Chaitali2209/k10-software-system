from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QFrame, QVBoxLayout
from PySide6.QtCore import QUrl


class MapWidget(QFrame):

    def __init__(self):
        super().__init__()

        self.web = QWebEngineView()
        self.web.load(QUrl("http://127.0.0.1:8000/map.html"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.web)

    # -------------------------
    # UPDATE DRONE POSITION
    # -------------------------
    def update_position(self, telemetry):

        if "lat" in telemetry and "lon" in telemetry:
            self.web.page().runJavaScript(
                f"updateDronePosition({telemetry['lat']}, {telemetry['lon']});"
            )

    # -------------------------
    # ENABLE MISSION PLANNING
    # -------------------------
    def enable_mission_planning(self):

        self.web.page().runJavaScript(
            "enableMissionPlanning();"
        )

    # -------------------------
    # UPLOAD MISSION
    # -------------------------
    def upload_mission(self):

        self.web.page().runJavaScript(
            "uploadMission();"
        )

    # -------------------------
    # CLEAR USER MISSION
    # -------------------------
    def clear_mission(self):

        self.web.page().runJavaScript(
            "clearMission();"
        )

    # -------------------------
    # CLEAR DRONE PATH (OSD)
    # -------------------------
    def clear_path(self):

        self.web.page().runJavaScript(
            "clearPath();"
        )