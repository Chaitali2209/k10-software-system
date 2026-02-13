# ocr/osd_extractor.py

import cv2
import re
import easyocr
import numpy as np

# -------------------------------------------------
# Create ONE global EasyOCR reader (CRITICAL)
# -------------------------------------------------
# This must be created once and reused
reader = easyocr.Reader(
    ['en'],
    gpu=True,          # Uses your RTX 4060
    verbose=False
)

# -------------------------------------------------
# Telemetry parsing (unchanged logic)
# -------------------------------------------------
def parse(text: str) -> dict:
    data = {}

    lat = re.search(r'Lat[:\s]*([-+]?\d+\.\d+)', text, re.IGNORECASE)
    lon = re.search(r'Lon[:\s]*([-+]?\d+\.\d+)', text, re.IGNORECASE)
    alt = re.search(r'Alt[:\s]*([\d\.]+)', text, re.IGNORECASE)
    bat = re.search(r'Bat[:\s]*([\d\.]+)', text, re.IGNORECASE)
    sats = re.search(r'Sats[:\s]*(\d+)', text, re.IGNORECASE)
    hdop = re.search(r'HDOP[:\s]*([\d\.]+)', text, re.IGNORECASE)

    if lat:  data["lat"] = lat.group(1)
    if lon:  data["lon"] = lon.group(1)
    if alt:  data["alt"] = alt.group(1)
    if bat:  data["bat"] = bat.group(1)
    if sats: data["sats"] = sats.group(1)
    if hdop: data["hdop"] = hdop.group(1)

    return data


# -------------------------------------------------
# OCR helper
# -------------------------------------------------
def ocr_image(img: np.ndarray) -> str:
    """
    img: BGR or grayscale image
    returns: concatenated OCR text
    """
    if img is None or img.size == 0:
        return ""

    # EasyOCR works best on grayscale / high-contrast
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Light preprocessing (safe for OSD)
    img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_LINEAR)

    results = reader.readtext(
        img,
        detail=0,     # return text only
        paragraph=True
    )

    return " ".join(results)


# -------------------------------------------------
# Main entry point (used by VideoWorker)
# -------------------------------------------------
def extract_osd(top_osd, bottom_osd) -> dict:
    text_top = ocr_image(top_osd)
    text_bot = ocr_image(bottom_osd)

    combined_text = f"{text_top} {text_bot}"
    return parse(combined_text)
