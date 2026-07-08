import re
from typing import List, Dict

# Patterns that indicate a new section starts
SECTION_PATTERNS = [
    r'\n\s*(?:Section|SECTION|Sec\.)\s+\d+[\w\-\.]*',
    r'\n\s*\d+\.\s+[A-Z][a-z]',          # Numbered clauses like "14. Duties of..."
    r'\n\s*(?:CHAPTER|Chapter)\s+[IVXLC\d]+',
    r'\n\s*(?:PART|Part)\s+[IVXLC\d]+',
    r'\n\s*(?:Rule|RULE)\s+\d+',
]

COMBINED_PATTERN = '|'.join(SECTION_PATTERNS)

MIN_CHUNK_LENGTH = 80    # characters — skip tiny fragments
MAX_CHUNK_LENGTH = 2000  # characters — split very long sections


def chunk_by_section(text: str, base_metadata: dict) -> List[Dict]:
    """
    Split legal text on section boundaries.
    Returns list of {text, metadata} dicts ready for ChromaDB.
    """
    # Split on section headers, keeping the delimiter
    parts = re.split(f'({COMBINED_PATTERN})', text)

    # Re-join header with its body
    chunks_raw = []
    i = 0
    while i < len(parts):
        if re.match(COMBINED_PATTERN, parts[i]):
            # Header + body
            body = parts[i + 1] if i + 1 < len(parts) else ""
            chunks_raw.append(parts[i] + body)
            i += 2
        else:
            if parts[i].strip():
                chunks_raw.append(parts[i])
            i += 1

    chunks = []
    for raw in chunks_raw:
        raw = raw.strip()
        if len(raw) < MIN_CHUNK_LENGTH:
            continue

        # Very long sections get split further on paragraph boundaries
        if len(raw) > MAX_CHUNK_LENGTH:
            sub_chunks = split_long_section(raw)
        else:
            sub_chunks = [raw]

        for sub in sub_chunks:
            section_ref = extract_section_ref(sub)
            chunks.append({
                "text": sub.strip(),
                "metadata": {
                    **base_metadata,
                    "section_ref": section_ref,
                }
            })

    return chunks


def extract_section_ref(text: str) -> str:
    """Pull section number from the start of a chunk."""
    match = re.match(
        r'((?:Section|Sec\.|SECTION|Rule|RULE|Chapter|CHAPTER)\s+[\d\w\-\.]+)',
        text.strip()
    )
    return match.group(1).strip() if match else "General"


def split_long_section(text: str, max_len: int = MAX_CHUNK_LENGTH) -> List[str]:
    """Split oversized sections on paragraph breaks."""
    paragraphs = re.split(r'\n\s*\n', text)
    result, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) > max_len and current:
            result.append(current.strip())
            current = para
        else:
            current += "\n\n" + para
    if current.strip():
        result.append(current.strip())
    return result if result else [text]