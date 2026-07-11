import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import fitz
from corpus.corpus_config import CORPUS_CONFIG

CORPUS_ROOT = Path("corpus/")

def test_all_pdfs():
    print("\nVerifying corpus PDFs...\n")
    found, missing, broken = [], [], []

    for rel_path in CORPUS_CONFIG:
        full_path = CORPUS_ROOT / rel_path
        if not full_path.exists():
            missing.append(rel_path)
            print(f"  MISSING  {rel_path}")
            continue
        try:
            doc = fitz.open(str(full_path))
            text = "".join(p.get_text() for p in doc)
            doc.close()
            char_count = len(text.strip())
            status = "OK" if char_count > 200 else "WARN (low text — may need OCR)"
            found.append(rel_path)
            print(f"  {status:30s} {rel_path} ({char_count} chars)")
        except Exception as e:
            broken.append(rel_path)
            print(f"  ERROR    {rel_path} — {e}")

    print(f"\nFound:   {len(found)}")
    print(f"Missing: {len(missing)}")
    print(f"Broken:  {len(broken)}")

    if missing:
        print("\nDownload these PDFs:")
        for p in missing:
            config = CORPUS_CONFIG[p]
            print(f"  {p}")
            print(f"  → {config.get('source_url', 'No URL in config')}")

if __name__ == "__main__":
    test_all_pdfs()