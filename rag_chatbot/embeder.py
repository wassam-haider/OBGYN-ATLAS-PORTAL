"""
Embed chunks.jsonl (produced by rag_pipeline.py) using OpenRouter's OpenAI embedding
model, and upsert the results into a Chroma Cloud collection.

Setup required before running:
    pip install chromadb requests python-dotenv
    .env file in the same folder with:
        CHROMA_API_KEY=...
        CHROMA_TENANT=...
        CHROMA_DATABASE=...
        OPENROUTER_API_KEY=...

Usage:
    python embed_to_chroma.py chunks.jsonl fcps_gyn_notes
"""

import json
import os
import sys
import time
from typing import List, Dict, Any

import requests
from dotenv import load_dotenv
import chromadb

load_dotenv(override=True)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = "openai/text-embedding-3-small"  # 1536-dim, cheap, good default for RAG
OPENROUTER_EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"

BATCH_SIZE = 50          # texts per embedding API call
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 2
MAX_DOC_BYTES = 16000    # safety margin under Chroma Cloud's 16384-byte per-document quota


def load_chunks(jsonl_path: str) -> List[Dict[str, Any]]:
    chunks = []
    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def sanitize_metadata(chunk: Dict[str, Any]) -> Dict[str, Any]:
    """Chroma metadata values must be str/int/float/bool -- no lists/dicts.
    section_path is a list, so flatten it to a single readable string."""
    section_path = chunk.get("section_path", [])
    return {
        "source_file": chunk.get("source_file", ""),
        "archetype": chunk.get("archetype", ""),
        "section_path": " > ".join(section_path) if isinstance(section_path, list) else str(section_path),
        "chunk_index": chunk.get("chunk_index", 0),
        "token_count": chunk.get("token_count", 0),
    }


def make_chunk_id(chunk: Dict[str, Any], sub_index: int = None) -> str:
    safe_source = chunk.get("source_file", "unknown").replace(" ", "_").replace("/", "_")
    base = f"{safe_source}__{chunk.get('chunk_index', 0)}"
    return base if sub_index is None else f"{base}__{sub_index}"


def split_oversized(text: str, max_bytes: int = MAX_DOC_BYTES) -> List[str]:
    """Split text into pieces that fit under the byte limit.
    Tries to break on paragraph boundaries first, then falls back to a raw
    byte-safe character cut so multi-byte UTF-8 characters are never split
    mid-codepoint."""
    if len(text.encode("utf-8")) <= max_bytes:
        return [text]

    paragraphs = text.split("\n\n")
    pieces = []
    current = ""
    for para in paragraphs:
        candidate = (current + "\n\n" + para) if current else para
        if len(candidate.encode("utf-8")) <= max_bytes:
            current = candidate
        else:
            if current:
                pieces.append(current)
            # paragraph itself may be oversized -- hard-cut it
            if len(para.encode("utf-8")) > max_bytes:
                remaining = para
                while len(remaining.encode("utf-8")) > max_bytes:
                    cut = max_bytes
                    while len(remaining[:cut].encode("utf-8")) > max_bytes:
                        cut -= 50
                    pieces.append(remaining[:cut])
                    remaining = remaining[cut:]
                current = remaining
            else:
                current = para
    if current:
        pieces.append(current)
    return pieces


def get_existing_ids(collection, candidate_ids: List[str]) -> set:
    """Return the subset of candidate_ids already present in the collection."""
    if not candidate_ids:
        return set()
    try:
        result = collection.get(ids=candidate_ids)
        return set(result.get("ids", []))
    except Exception as e:
        print(f"  Warning: could not check existing ids ({e}); assuming none exist.")
        return set()


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Call OpenRouter's embeddings endpoint for a batch of texts, with basic retry."""
    payload = {"model": EMBEDDING_MODEL, "input": texts}
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.post(OPENROUTER_EMBEDDINGS_URL, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # OpenAI-style response: data["data"] is a list of {embedding, index}
            sorted_items = sorted(data["data"], key=lambda x: x["index"])
            return [item["embedding"] for item in sorted_items]
        except Exception as e:
            last_error = e
            print(f"  Batch embedding attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS * attempt)
    raise RuntimeError(f"Embedding failed after {MAX_RETRIES} attempts: {last_error}")


def main(jsonl_path: str, collection_name: str):
    if not OPENROUTER_API_KEY:
        raise EnvironmentError("OPENROUTER_API_KEY not found -- check your .env file.")

    print("Loading chunks...")
    raw_chunks = load_chunks(jsonl_path)
    print(f"Loaded {len(raw_chunks)} chunks from {jsonl_path}")

    # Expand any oversized chunk into byte-safe sub-chunks, each with its own id.
    expanded = []  # list of (id, text, metadata)
    oversized_count = 0
    for chunk in raw_chunks:
        text = chunk["text"]
        pieces = split_oversized(text)
        if len(pieces) > 1:
            oversized_count += 1
        meta = sanitize_metadata(chunk)
        if len(pieces) == 1:
            expanded.append((make_chunk_id(chunk), pieces[0], meta))
        else:
            for sub_i, piece in enumerate(pieces):
                sub_meta = dict(meta)
                sub_meta["split_part"] = sub_i
                expanded.append((make_chunk_id(chunk, sub_i), piece, sub_meta))

    if oversized_count:
        print(f"Split {oversized_count} oversized chunk(s) into byte-safe sub-chunks "
              f"({len(raw_chunks)} chunks -> {len(expanded)} documents to upsert).")

    print("Connecting to Chroma Cloud...")
    client = chromadb.CloudClient(
        tenant=os.getenv("CHROMA_TENANT"),
        database=os.getenv("CHROMA_DATABASE"),
        api_key=os.getenv("CHROMA_API_KEY"),
    )
    collection = client.get_or_create_collection(name=collection_name)
    print(f"Using collection: {collection_name}")

    total = len(expanded)
    skipped_total = 0
    for start in range(0, total, BATCH_SIZE):
        batch = expanded[start:start + BATCH_SIZE]
        batch_ids_all = [item[0] for item in batch]

        existing = get_existing_ids(collection, batch_ids_all)
        pending = [item for item in batch if item[0] not in existing]
        skipped_total += len(batch) - len(pending)

        batch_num = start // BATCH_SIZE + 1
        if not pending:
            print(f"Batch {batch_num} ({start + 1}-{min(start + BATCH_SIZE, total)} of {total}): "
                  f"already in collection, skipping.")
            continue

        ids = [item[0] for item in pending]
        texts = [item[1] for item in pending]
        metadatas = [item[2] for item in pending]

        print(f"Embedding batch {batch_num} "
              f"({start + 1}-{min(start + BATCH_SIZE, total)} of {total}, "
              f"{len(pending)} new / {len(batch) - len(pending)} skipped)...")
        embeddings = embed_batch(texts)

        collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    print(f"Done. {total} documents processed, {skipped_total} skipped (already present), "
          f"{total - skipped_total} embedded and stored in Chroma Cloud collection '{collection_name}'.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python embed_to_chroma.py <chunks.jsonl> <collection_name>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])