from ultralytics import YOLO
import torch
import cv2
import numpy as np


class YOLOOBBDetector:
    def __init__(self, model_path,
                 conf=0.5,
                 tracker="botsort.yaml",
                 imgsz=640):

        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.conf = conf
        self.tracker = tracker
        self.imgsz = imgsz

        # Load model
        self.model = YOLO(model_path)
        self.model.to(self.device)

        print(f"[YOLO] Loaded on: {self.device}")
        if self.device != "cpu":
            print("[YOLO] GPU:", torch.cuda.get_device_name(0))

    def infer(self, frame):

        results = self.model.track(
            frame,
            task="obb",
            conf=self.conf,
            device=self.device,
            imgsz=self.imgsz,
            tracker=self.tracker,
            verbose=False,
            persist=True
        )

        result = results[0]
        annotated_frame = frame.copy()

        if result.obb is not None:
            boxes = result.obb.xyxyxyxy.cpu().numpy()  # 8-point OBB format
            cls_ids = result.obb.cls.cpu().numpy()

            for i, box in enumerate(boxes):

                pts = box.reshape((4, 2)).astype(int)

                # -------- Customize here --------
                color = (0, 0, 255)      # RED (BGR)
                thickness = 4            # Increase width here
                # --------------------------------

                cv2.polylines(
                    annotated_frame,
                    [pts],
                    isClosed=True,
                    color=color,
                    thickness=thickness
                )

        return annotated_frame