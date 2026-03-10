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
DEBUG_SAVE_IMAGES = True

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

def reconstruct_bat(batraw):
    digit = ''
    if len(batraw) > 2:
        digit = batraw[:2] + '.' + batraw[2:]
        return digit
    else:
        return digit.join(batraw)
    
def reconstruct_sat(sats):
    return sats[:2]

# -------------------------------------------------
# Preprocessing
# -------------------------------------------------

def preprocess(img):

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Strong upscale
    gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)

    # Slight blur only to remove sensor noise (not strong)
    gray = cv2.GaussianBlur(gray, (3,3), 0)

    # High threshold (digits are bright)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    # Morphological closing to connect thin strokes
    kernel = np.ones((2,2), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    return thresh


# -------------------------------------------------
# MAIN EXTRACTION FUNCTION
# -------------------------------------------------

def extract_osd(frame):

    data = {}
    h, w = frame.shape[:2]

    # # ------------------------- DIGITAL OSD EXTRACTION -------------------------
    # # YOUR FIXED PIXEL ROIs for DIGITAL OSD (based on IIT Bombay's OSD layout)
    # # -------------------------
    # LAT = top-right 25% width, 6% height
    lat_roi = frame[
        int(0.01 * h): int(0.06 * h),
        int(0.77 * w): int(0.97 * w)
    ]

    # LON = top-left
    #  25% width, 6% height
    lon_roi = frame[
        int(0.01 * h): int(0.06 * h),
        int(0.06 * w): int(0.30 * w)
    ]

    alt_roi = frame[
        int(0.07 * h) : int(0.11 * h),
        int(0.06 * w) : int(0.12 * w)
    ]

    speed_roi = frame[
        int(0.07 * h) : int(0.11 * h),
        int(0.77 * w): int(0.83 * w)
    ]

    sats_roi = frame[
        int(0.01 * h): int(0.06 * h),
        int(0.7 * w): int(0.74 * w)
    ]

    bat_roi = frame[
        int(0.87 * h): int(0.92*h),
        int(0.7 * w): int(0.78 * w)
    ]

        # ------------------------- ANALOG OSD EXTRACTION -------------------------
    # YOUR FIXED PIXEL ROIs for DIGITAL OSD (based on IIT Bombay's OSD layout)
    # -------------------------
    # LAT = top-right 25% width, 6% height
    # lon_roi = frame[
    #     int(0.02 * h): int(0.10 * h),
    #     int(0.58 * w): int(0.97 * w)
    # ]

    # # LON = top-left 25% width, 6% height
    # lat_roi = frame[
    #     int(0.02 * h): int(0.10 * h),
    #     int(0.08 * w): int(0.41 * w)
    # ]


    # lat_img = preprocess(lat_roi)
    # lon_img = preprocess(lon_roi)
    
    lat_img = lat_roi
    lon_img = lon_roi
    alt_img = alt_roi
    speed_img = speed_roi
    sats_img = sats_roi
    bat_img = bat_roi

    if DEBUG_SAVE_IMAGES:
        cv2.imwrite("lat_debug.png", lat_img)
        cv2.imwrite("lon_debug.png", lon_img)
        cv2.imwrite("alt_debug.png", alt_img)
        cv2.imwrite("speed_debug.png", speed_img)
        cv2.imwrite("sats_debug.png", sats_img)
        cv2.imwrite("bat_debug.png", bat_img)

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

    alt_raw = reader.readtext(
        alt_img,
        detail=0,
        paragraph=False,
        allowlist="0123456789"
    )

    speed_raw = reader.readtext(
        speed_img,
        detail=0,
        paragraph=False,
        allowlist="0123456789"
    )

    sats_raw = reader.readtext(
        sats_img,
        detail=0,
        paragraph=False,
        allowlist="0123456789"
    )

    bat_raw = reader.readtext(
        bat_img,
        detail=0,
        paragraph=False,
        allowlist="0123456789"
    )

    lat_text = "".join(lat_raw)
    lon_text = "".join(lon_raw)
    alt_text = "".join(alt_raw)
    speed_text = "".join(speed_raw)
    sats_text = "".join(sats_raw)
    bat_text = "".join(bat_raw)

    print("\n[RAW LAT]:", lat_text)
    print("[RAW LON]:", lon_text)
    print("[RAW ALT]:", alt_text)
    print("[RAW SPEED]:", speed_text)
    print("[RAW SATS]:", sats_text)
    print("[RAW BAT]:", bat_text)

    lat = reconstruct_lat(lat_text)
    lon = reconstruct_lon(lon_text)
    bat_text = reconstruct_bat(bat_text)
    sats_text = reconstruct_sat(sats_text)

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

        if alt_text != "":
            data["alt"] = alt_text
        
        if speed_text != "":
            data["speed"] = speed_text
        
        if sats_text != "":
            data["sats"] = sats_text
        
        if bat_text != "":
            data["bat"] = bat_text

        if valid_lat(lat_smoothed) and valid_lon(lon_smoothed):
            data["lat"] = lat_smoothed
            data["lon"] = lon_smoothed
            

            print("[SMOOTHED]:", lat_smoothed, lon_smoothed)

    return data