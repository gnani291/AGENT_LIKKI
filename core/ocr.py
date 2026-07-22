"""
ocr.py
Image -> text extraction. Plain pytesseract by default, with an optional
OpenCV preprocessing pass (grayscale + adaptive threshold) that usually
improves accuracy on noisy / low-contrast screenshots and photos.
"""

import numpy as np
import pytesseract
from PIL import Image


def extract_text_from_image(image: Image.Image, enhance: bool = True) -> str:
    try:
        if enhance:
            import cv2

            img_array = np.array(image.convert("RGB"))
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            gray = cv2.GaussianBlur(gray, (5, 5), 0)
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            config = r"--oem 3 --psm 6"
            return pytesseract.image_to_string(thresh, config=config).strip()

        return pytesseract.image_to_string(image).strip()

    except Exception as e:
        print("OCR error:", e)
        return ""
