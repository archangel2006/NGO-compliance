import os, json, hashlib
from datetime import datetime
from pathlib import Path
import fitz  # PyMuPDF
import chromadb
import ollama

# Add project root to path
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))

from corpus.corpus_config import CORPUS_CONFIG, REQUIRED_CORPUS
from backend.utils.chunker import chunk_by_section

CORPUS_ROOT    = Path("corpus/")
METADATA_ROOT  = Path("corpus_metadata/")
VECTORSTORE    = Path("vectorstore/")
EMBED_MODEL    = "nomic-embed-text"
COLLECTION     = "legal_corpus"

chroma_client = chromadb.PersistentClient(path=str(VECTORSTORE))
collection    = chroma_client.get_or_create_collection(
    name=COLLECTION,
    metadata={"hnsw:space": "cosine"}  # cosine similarity for legal text
)


def extract_text_from_pdf(pdf_path: Path) -> str:
    doc = fitz.open(str(pdf_path))
    pages = []
    for page in doc:
        text = page.get_text()
        if text.strip():
            pages.append(text)
    doc.close()
    return "\n".join(pages)


def embed_text(text: str) -> list:
    """Get embedding from Ollama nomic-embed-text."""
    response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
    return response["embedding"]


def ingest_pdf(rel_path: str, config: dict) -> int:
    """
    Ingest one PDF into ChromaDB.
    Returns number of NEW chunks added (0 if already ingested).
    """
    full_path = CORPUS_ROOT / rel_path
    if not full_path.exists():
        print(f"  ⚠  MISSING: {rel_path}")
        return -1

    raw_text = extract_text_from_pdf(full_path)
    if len(raw_text.strip()) < 100:
        print(f"  ⚠  Almost empty text extracted — may need OCR: {rel_path}")

    chunks = chunk_by_section(raw_text, base_metadata={
        "act_name":   config["act_name"],
        "jurisdiction": config["jurisdiction"],
        "state":      ",".join(config["applicable_states"]),
        "rel_path":   rel_path,
    })

    ids, texts, metas, embeds = [], [], [], []

    for i, chunk in enumerate(chunks):
        chunk_id = f"{hashlib.md5(rel_path.encode()).hexdigest()[:8]}_{i}"

        # Skip if already in ChromaDB (idempotent)
        if collection.get(ids=[chunk_id])["ids"]:
            continue

        embedding = embed_text(chunk["text"])
        ids.append(chunk_id)
        texts.append(chunk["text"])
        metas.append(chunk["metadata"])
        embeds.append(embedding)

    if ids:
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metas,
            embeddings=embeds
        )

    # Save metadata JSON
    save_metadata(rel_path, config, len(chunks), len(ids))
    return len(ids)


def save_metadata(rel_path: str, config: dict, total_chunks: int, new_chunks: int):
    meta_path = METADATA_ROOT / rel_path.replace(".pdf", ".json")
    meta_path.parent.mkdir(parents=True, exist_ok=True)

    existing = {}
    if meta_path.exists():
        with open(meta_path) as f:
            existing = json.load(f)

    metadata = {
        **existing,
        **config,
        "filename":     os.path.basename(rel_path),
        "ingested":     True,
        "ingested_date": datetime.now().isoformat(),
        "total_chunks": total_chunks,
        "new_chunks":   new_chunks,
    }
    with open(meta_path, "w") as f:
        json.dump(metadata, f, indent=2)


def ingest_all(force: bool = False):
    """Ingest all PDFs in corpus_config. Safe to re-run."""
    print(f"\nStarting corpus ingestion — {len(CORPUS_CONFIG)} documents\n")
    results = {"ingested": 0, "skipped": 0, "missing": 0, "errors": 0}

    for rel_path, config in CORPUS_CONFIG.items():
        print(f"→ {rel_path}")
        try:
            count = ingest_pdf(rel_path, config)
            if count == -1:
                results["missing"] += 1
            elif count == 0:
                print(f"  ✓ Already ingested")
                results["skipped"] += 1
            else:
                print(f"  ✓ {count} new chunks")
                results["ingested"] += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results["errors"] += 1

    print(f"\n{'='*50}")
    print(f"Ingested:  {results['ingested']} new docs")
    print(f"Skipped:   {results['skipped']} (already ingested)")
    print(f"Missing:   {results['missing']} PDFs not found")
    print(f"Errors:    {results['errors']}")
    print(f"Total chunks in ChromaDB: {collection.count()}")


def check_coverage(state: str) -> list:
    """Returns list of missing required PDFs for a state."""
    required = REQUIRED_CORPUS.get(state, [])
    missing = []
    for rel_path in required:
        meta_path = METADATA_ROOT / rel_path.replace(".pdf", ".json")
        if not meta_path.exists():
            missing.append(rel_path)
        else:
            with open(meta_path) as f:
                meta = json.load(f)
            if not meta.get("ingested"):
                missing.append(rel_path)
    return missing


if __name__ == "__main__":
    ingest_all()