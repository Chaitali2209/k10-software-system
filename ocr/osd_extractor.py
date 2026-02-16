# ocr/osd_extractor.py

import cv2
import easyocr
import re
import torch
from collections import deque
import numpy as np

# -------------------------------------------------
# EasyOCR init (once)
# -------------------------------------------------
reader = easyocr.Reader(
    ['en'],
    gpu=torch.cuda.is_available(),
    verbose=False
)

# -------------------------------------------------
# IIT Bombay Bounding Box (VERY IMPORTANT)
# -------------------------------------------------
MIN_LAT = 19.1300
MAX_LAT = 19.1400

MIN_LON = 72.9050
MAX_LON = 72.9200

# Smoothing buffers
lat_buffer = deque(maxlen=5)
lon_buffer = deque(maxlen=5)

# -------------------------------------------------
# Validation
# -------------------------------------------------

def valid_lat(lat):
    return MIN_LAT <= lat <= MAX_LAT

def valid_lon(lon):
    return MIN_LON <= lon <= MAX_LON


# -------------------------------------------------
# Digit Reconstruction
# -------------------------------------------------

def reconstruct_lat(text):
    """
    Converts:
    191346074 → 19.1346074
    Handles minor OCR corruption
    """
    digits = re.sub(r'\D', '', text)

    if len(digits) < 9:
        return None

    # Force structure 19.xxxxxxx
    if not digits.startswith("19"):
        return None

    lat_str = digits[:2] + "." + digits[2:9]

    try:
        lat = float(lat_str)
        if valid_lat(lat):
            return lat
    except:
        pass

    return None


def reconstruct_lon(text):
    """
    Converts:
    729129807 → 72.9129807
    """
    digits = re.sub(r'\D', '', text)

    if len(digits) < 9:
        return None

    if not digits.startswith("72"):
        return None

    lon_str = digits[:2] + "." + digits[2:9]

    try:
        lon = float(lon_str)
        if valid_lon(lon):
            return lon
    except:
        pass

    return None


# -------------------------------------------------
# Preprocessing
# -------------------------------------------------

def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Upscale strongly (OSD fonts are small)
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # Increase contrast
    gray = cv2.equalizeHist(gray)

    # Light blur
    gray = cv2.GaussianBlur(gray, (3,3), 0)

    # Threshold
    _, thresh = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    return thresh


# -------------------------------------------------
# MAIN EXTRACTION FUNCTION
# -------------------------------------------------

def extract_osd(frame):

    data = {}

    # -------------------------
    # YOUR FIXED PIXEL ROIs
    # -------------------------
    lat_roi = frame[1:55, 1477:1854]
    lon_roi = frame[0:55, 107:475]

    lat_img = preprocess(lat_roi)
    lon_img = preprocess(lon_roi)

    lat_raw = reader.readtext(
        lat_img,
        detail=0,
        paragraph=False,
        allowlist="0123456789"
    )

    lon_raw = reader.readtext(
        lon_img,
        detail=0,
        paragraph=False,
        allowlist="0123456789"
    )

    lat_text = "".join(lat_raw)
    lon_text = "".join(lon_raw)

    print("\n[RAW LAT]:", lat_text)
    print("[RAW LON]:", lon_text)

    lat = reconstruct_lat(lat_text)
    lon = reconstruct_lon(lon_text)

    # -------------------------
    # Smoothing + Validation
    # -------------------------
    if lat is not None:
        lat_buffer.append(lat)

    if lon is not None:
        lon_buffer.append(lon)

    if len(lat_buffer) >= 3 and len(lon_buffer) >= 3:

        # Median smoothing (very robust to spikes)
        lat_smoothed = float(np.median(lat_buffer))
        lon_smoothed = float(np.median(lon_buffer))

        if valid_lat(lat_smoothed) and valid_lon(lon_smoothed):
            data["lat"] = lat_smoothed
            data["lon"] = lon_smoothed

            print("[SMOOTHED]:", lat_smoothed, lon_smoothed)

    return data
