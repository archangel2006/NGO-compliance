import cv2
import numpy as np
from PIL import Image


def preprocess_for_ocr(image) -> np.ndarray:
    """
    Full preprocessing pipeline for scanned documents.
    Input: PIL Image or numpy array.
    Output: cleaned numpy array ready for Tesseract.
    """
    # Convert PIL → numpy
    if isinstance(image, Image.Image):
        img = np.array(image)
    else:
        img = image.copy()

    # Convert to grayscale
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # Scale up if resolution is low
    h, w = gray.shape[:2]
    if w < 1500:
        scale  = 2.0
        gray   = cv2.resize(gray, None, fx=scale, fy=scale,
                            interpolation=cv2.INTER_CUBIC)

    # Deskew
    gray = _deskew(gray)

    # Denoise
    gray = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7,
                                     searchWindowSize=21)

    # Binarize — Otsu's adaptive threshold works well on stamps/watermarks
    _, binary = cv2.threshold(gray, 0, 255,
                              cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Remove tiny noise blobs (salt and pepper)
    kernel  = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    return cleaned


def _deskew(gray: np.ndarray) -> np.ndarray:
    """Detect and correct page skew."""
    coords = np.column_stack(np.where(gray > 0))
    if len(coords) < 10:
        return gray

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    if abs(angle) < 0.3:  # already straight enough
        return gray

    h, w = gray.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h),
                          flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)