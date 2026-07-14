import io
import fitz              # PyMuPDF
import pytesseract
from PIL import Image
from pathlib import Path
from backend.services.preprocessing import preprocess_for_ocr

# Language packs per state — install via: apt-get install tesseract-ocr-hin etc.
LANG_MAP = {
    "maharashtra": "eng+mar",
    "delhi":       "eng+hin",
    "karnataka":   "eng+kan",
    "rajasthan":   "eng+hin",
    "central":     "eng",
}

MIN_TEXT_LENGTH  = 20   # chars per page — below this, treat as scanned
TESSERACT_CONFIG = "--psm 6 --oem 3"   # psm 6 = assume uniform block of text


def extract_text(pdf_path: str, state: str = "central") -> dict:
    """
    Main OCR entry point.
    Tries PyMuPDF direct extraction first (fast, perfect for digital PDFs).
    Falls back to Tesseract for scanned pages.
    
    Returns dict with full text + quality metadata.
    """
    path  = Path(pdf_path)
    lang  = LANG_MAP.get(state.lower(), "eng")
    doc   = fitz.open(str(path))

    pages_text   = []
    pages_method = []

    for page in doc:
        # Attempt 1: direct text extraction
        direct_text = page.get_text().strip()

        if len(direct_text) >= MIN_TEXT_LENGTH:
            pages_text.append(direct_text)
            pages_method.append("pymupdf")
        else:
            # Attempt 2: render page as image → Tesseract
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes("png")))

            cleaned   = preprocess_for_ocr(img)
            ocr_text  = pytesseract.image_to_string(
                cleaned, lang=lang, config=TESSERACT_CONFIG
            ).strip()

            pages_text.append(ocr_text)
            pages_method.append("tesseract")

    doc.close()

    full_text    = "\n\n".join(pages_text)
    method_used  = "mixed" if len(set(pages_method)) > 1 else pages_method[0] if pages_method else "none"
    quality      = _assess_quality(full_text)

    return {
        "text":         full_text,
        "method":       method_used,
        "page_count":   len(pages_text),
        "char_count":   len(full_text),
        "quality":      quality,
        "pages_method": pages_method,   # per-page breakdown
    }


def _assess_quality(text: str) -> str:
    """Rough quality check on extracted text."""
    if len(text) < 200:
        return "poor"
    # Check for garbled OCR (too many non-ASCII or repeated chars)
    non_ascii = sum(1 for c in text if ord(c) > 127)
    if non_ascii / max(len(text), 1) > 0.3:
        return "poor"
    if len(text) > 2000:
        return "good"
    return "fair"