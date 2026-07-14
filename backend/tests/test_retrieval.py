import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

import chromadb
import ollama

VECTORSTORE = Path("vectorstore/")
EMBED_MODEL  = "nomic-embed-text"

client     = chromadb.PersistentClient(path=str(VECTORSTORE))
collection = client.get_or_create_collection("legal_corpus")

TEST_QUERIES = [
    ("minimum members required society Maharashtra",       "maharashtra"),
    ("trustees governing body Public Trust Maharashtra",   "maharashtra"),
    ("FCRA registration foreign contribution bank account","all"),
    ("12A 80G income tax exemption charitable",            "all"),
    ("fund utilisation statement grant accounts",          "maharashtra"),
    ("audit chartered accountant ICAI",                    "all"),
    ("registration certificate Societies Act Delhi",       "delhi"),
]

def test_retrieval():
    total = collection.count()
    print(f"\nTotal chunks in ChromaDB: {total}")
    if total == 0:
        print("ERROR: ChromaDB is empty. Run ingest.py first.")
        return

    print("\nRunning test queries...\n")
    for query_text, state in TEST_QUERIES:
        print(f"Query: '{query_text}' [{state}]")

        embedding = ollama.embeddings(
            model=EMBED_MODEL, prompt=query_text
        )["embedding"]

        where_filter = (
            {"$or": [{"state": state}, {"state": "all"}]}
            if state != "all"
            else {}
        )

        results = collection.query(
            query_embeddings=[embedding],
            n_results=2,
            where=where_filter if where_filter else None
        )

        if not results["documents"][0]:
            print("  NO RESULTS — check if relevant PDFs are ingested\n")
            continue

        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            print(f"  -> {meta.get('act_name','?')} - {meta.get('section_ref','?')}")
            print(f"    {doc[:120].strip()}...")
        print()

if __name__ == "__main__":
    test_retrieval()