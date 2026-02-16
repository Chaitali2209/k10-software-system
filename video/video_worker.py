import cv2
from PySide6.QtCore import QThread, Signal
from ocr.osd_extractor import extract_osd
from ml.detector import YOLOOBBDetector

class VideoWorker(QThread):
    frame_signal = Signal(object)
    telemetry_signal = Signal(dict)

    def __init__(self, device_id=0):
        super().__init__()
        self.device_id = device_id
        self.cap = None
        self.source_type = "camera"   # or "file"
        self.video_path = None

        self.detector = YOLOOBBDetector("yolov8n-obb.pt")
        self.ai_enabled = False
        self.running = True
        self.frame_id = 0

        self._open_camera()

    def _open_camera(self):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(self.device_id, cv2.CAP_V4L2)
        self.source_type = "camera"

    def open_video_file(self, path):
        if self.cap:
            self.cap.release()
        self.cap = cv2.VideoCapture(path)
        self.video_path = path
        self.source_type = "file"

    def enable_ai(self, enabled):
        self.ai_enabled = enabled

    def run(self):
        while self.running:

            if not self.cap or not self.cap.isOpened():
                continue

            ret, frame = self.cap.read()

            # End of video → loop file
            if not ret:
                if self.source_type == "file":
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    continue

            # ---------------------------------------
            # OSD Extraction (using full frame now)
            # ---------------------------------------
            if self.frame_id % 10 == 0:   # every 10 frames
                telemetry = extract_osd(frame)
                if telemetry.get("lat") and telemetry.get("lon"):
                    print("[VALID TELEMETRY]", telemetry)
                    self.telemetry_signal.emit(telemetry)

            # ---------------------------------------
            # YOLO Region (exclude OSD if needed)
            # ---------------------------------------
            h, w, _ = frame.shape

            # Adjust this if your OSD is only top strip
            middle = frame[50:h, :]   # skip small top area if needed

            if self.ai_enabled:
                middle = self.detector.infer(middle)
                frame[50:h, :] = middle

            self.frame_signal.emit(frame)
            self.frame_id += 1
