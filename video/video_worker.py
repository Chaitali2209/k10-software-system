import cv2
from PySide6.QtCore import QThread, Signal
from ocr.osd_extractor import extract_osd
from ml.detector import YOLOOBBDetector
import time


class VideoWorker(QThread):

    frame_signal = Signal(object)
    telemetry_signal = Signal(dict)

    def __init__(self, device_id=1):   # 🔥 DEFAULT = CAMERA 1
        super().__init__()

        self.device_id = device_id
        self.cap = None
        self.source_type = "camera"
        self.video_path = None

        self.ai_enabled = False
        self.running = False
        self._thread_started = False

        # YOLO loads once
        self.detector = YOLOOBBDetector(
            "D:\\k10app_copy\\k10-software-system\\ml\\yolo-obb.pt"
        )

    # --------------------------------------------------
    # START STREAM
    # --------------------------------------------------
    def start_stream(self):

        if self.running:
            return

        print("[INFO] Starting stream")

        self.running = True
        self._open_source()

        if not self._thread_started:
            self.start()
            self._thread_started = True

    # --------------------------------------------------
    # STOP STREAM
    # --------------------------------------------------
    def stop_stream(self):

        print("[INFO] Stopping stream")

        self.running = False

        if self.cap:
            self.cap.release()
            self.cap = None

    # --------------------------------------------------
    # OPEN CAMERA OR FILE
    # --------------------------------------------------
    def _open_source(self):

        if self.cap:
            self.cap.release()
            self.cap = None

        time.sleep(0.2)

        if self.source_type == "camera":

            print(f"[INFO] Opening Camera {self.device_id}")

            # Try DirectShow
            cap = cv2.VideoCapture(self.device_id, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

            if not cap.isOpened():
                print("[WARN] DSHOW failed, trying MSMF")
                cap = cv2.VideoCapture(self.device_id, cv2.CAP_MSMF)

            self.cap = cap

        else:
            print("[INFO] Opening Video File")
            self.cap = cv2.VideoCapture(self.video_path)

        if not self.cap or not self.cap.isOpened():
            print("[ERROR] Failed to open source")

    # --------------------------------------------------
    # CHANGE CAMERA
    # --------------------------------------------------
    def change_camera(self, device_index):

        print(f"[INFO] Camera selected: {device_index}")

        self.device_id = device_index
        self.source_type = "camera"

        if self.running:
            self._open_source()

    # --------------------------------------------------
    # LOAD VIDEO FILE
    # --------------------------------------------------
    def open_video_file(self, path):

        print("[INFO] Video file selected")

        self.video_path = path
        self.source_type = "file"

        if self.running:
            self._open_source()

    # --------------------------------------------------
    # AI TOGGLE
    # --------------------------------------------------
    def enable_ai(self, enabled):
        self.ai_enabled = enabled
        print(f"[INFO] AI Enabled: {self.ai_enabled}")

    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------
    def run(self):

        last_ocr_time = 0

        while True:

            if not self.running:
                time.sleep(0.1)
                continue

            if not self.cap or not self.cap.isOpened():
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()

            if not ret or frame is None:
                if self.source_type == "file":
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    time.sleep(0.01)
                    continue

            # -------------------------------------------------
            # OCR
            # -------------------------------------------------
            if time.time() - last_ocr_time > 0.5:
                last_ocr_time = time.time()
                try:
                    telemetry = extract_osd(frame.copy())
                    if telemetry.get("lat") and telemetry.get("lon"):
                        self.telemetry_signal.emit(telemetry)
                except Exception as e:
                    print("[OCR ERROR]", e)

            # -------------------------------------------------
            # YOLO
            # -------------------------------------------------
            if self.ai_enabled:
                try:
                    frame = self.detector.infer(frame)
                except Exception as e:
                    print("[YOLO ERROR]", e)

            self.frame_signal.emit(frame)

            time.sleep(1 / 60)
