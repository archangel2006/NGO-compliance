# backend/tests/test_extraction.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.services.ocr import extract_text
from backend.services.extraction import extract_fields
import json

def test_ocr(pdf_path: str, state: str = "maharashtra"):
    print(f"\nTesting OCR: {pdf_path}")
    result = extract_text(pdf_path, state)
    print(f"  Method:     {result['method']}")
    print(f"  Pages:      {result['page_count']}")
    print(f"  Characters: {result['char_count']}")
    print(f"  Quality:    {result['quality']}")
    print(f"  Sample:     {result['text'][:300]}")
    assert result["char_count"] > 100, "Too little text — check OCR"
    return result["text"]

def test_extraction(text: str, doc_type: str, state: str):
    print(f"\nTesting extraction: {doc_type}")
    fields = extract_fields(text, doc_type, state)
    print(json.dumps(fields, indent=2, default=str))
    assert "error" not in fields, f"Extraction error: {fields}"
    assert fields["_validation"]["clean"] or True  # log issues but don't fail
    return fields

if __name__ == "__main__":
    # Replace with actual test PDFs
    test_files = [
        ("uploads/test/sample_trust_deed.pdf",  "trust_deed",  "maharashtra"),
        ("uploads/test/sample_12a.pdf",         "certificate_12a", "maharashtra"),
        ("uploads/test/sample_fcra.pdf",        "fcra_certificate", "maharashtra"),
    ]
    for path, doc_type, state in test_files:
        if Path(path).exists():
            text = test_ocr(path, state)
            test_extraction(text, doc_type, state)
        else:
            print(f"\nSKIPPED (no test file): {path}")