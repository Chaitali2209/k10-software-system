import cv2
from PySide6.QtCore import QThread, Signal
# from ocr.osd_extractor import extract_osd
from ml.detector import YOLOOBBDetector
import time
# from PySide6.QtCore import QThread
from threading import Thread
import os
# from ocr.osd_extractor import OCRWorker


class VideoWorker(QThread):

    frame_signal = Signal(object)
    # raw_frame_signal = Signal(object)
    telemetry_signal = Signal(dict)


    def __init__(self, device_id=1):   # 🔥 DEFAULT = CAMERA 1
        super().__init__()

        self.device_id = device_id
        self.cap = None
        self.source_type = "camera"
        self.video_path = None
        self.out = None

        self.ai_enabled = False
        self.running = False
        self._thread_started = False
        # self.ocr.telemetry_signal.connect(self.telemetryemit)
        # YOLO loads once
        self.detector = YOLOOBBDetector( # Path update for my system only, change as needed
             # "D:\\k10app_copy\\k10-software-system\\ml\\yolo-obb.pt"
            "D:\\k10app_copy\\k10-software-system\\ml\\best.pt"
            # "C:\\Users\\DEVELOPER\\Documents\\k10-software-system\\yolov8n-obb.pt"
            # "D:\\k10app_copy\\k10-software-system\\ml\\best-inf3.pt"
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
            self.out.release()
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
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            if not cap.isOpened():
                print("[WARN] DSHOW failed, trying MSMF")
                cap = cv2.VideoCapture(self.device_id, cv2.CAP_MSMF)
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

            self.cap = cap
            userpath = os.path.expanduser("~")
            videodir = os.path.join(userpath, "Videos")
            path = os.path.join(videodir, f"outputvid{int(time.time())}.mp4")
            self.out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
            # print(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        else:
            print("[INFO] Opening Video File")
            self.cap = cv2.VideoCapture(self.video_path)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            userpath = os.path.expanduser("~")
            videodir = os.path.join(userpath, "Videos")
            path = os.path.join(videodir, f"outputvid{int(time.time())}.mp4")
            self.out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'mp4v'), 20.0, (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
            # print(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
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
    
    def fetch_frame(self):
        """Process frames with AI in a separate thread."""
        while True:
            if self.ai_enabled and hasattr(self, 'frame') and self.frame is not None:
                try:
                    self.detect_frame = self.detector.infer(cv2.resize(self.frame, (1280, 720)))
                except Exception as e:
                    print("[YOLO ERROR]", e)
            # time.sleep(0.01)  # Prevent CPU spinning
    def telemetryemit(self, data):
        self.telemetry_signal.emit(data)
    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------
    def run(self):

        # last_ocr_time = 0

        # Start AI thread as daemon so it doesn't block
        # ai = Thread(target=self.fetch_frame, daemon=True)   
        # ai.start()
        
        while True:

            if not self.running:
                time.sleep(0.1)
                continue

            if not self.cap or not self.cap.isOpened():
                time.sleep(0.1)
                continue

            ret, frame = self.cap.read()
            self.out.write(frame)
            frame =cv2.resize(frame, (1080, 608))

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
            
            # if time.time() - last_ocr_time > 1:
            #     last_ocr_time = time.time()
            #     try:
            #         # telemetry = OCRWorker(frame.copy())
            #         # # if telemetry.get("lat") and telemetry.get("lon"):
            #         # self.telemetry_signal.emit(telemetry)
            #         self.ocr = OCRWorker(frame.copy())
                    
            #     except Exception as e:
            #         print("[OCR ERROR]", e)

            # # Emit raw frame (for plain video window)
            # self.raw_frame_signal.emit(cv2.resize(self.frame, (1280, 720)))

            # # Emit processed frame (with AI annotations if enabled)
            # if self.ai_enabled and hasattr(self, 'detect_frame') and self.detect_frame is not None:
            #     self.frame_signal.emit(cv2.resize(self.detect_frame, (1280, 720)))
            # else:
            #     self.frame_signal.emit(cv2.resize(self.frame, (1280, 720)))

            
            if self.ai_enabled:
                try:
                    frame = self.detector.infer(frame)
                except Exception as e:
                    print("[YOLO ERROR]", e)
            self.frame_signal.emit(frame)

            time.sleep(1 / 60)
        