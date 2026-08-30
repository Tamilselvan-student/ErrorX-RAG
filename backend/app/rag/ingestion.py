"""Document ingestion pipeline: markdown files -> chunks -> embeddings -> ChromaDB.

The database is persisted locally and only rebuilt when:

* the collection is empty, or
* ``force=True`` is passed.

This prevents unnecessary regeneration on every application start.
"""
import logging
import time
from typing import List, Optional

from app.config import get_settings

from .chunker import CHUNK_SIZE, CHUNK_OVERLAP, chunk_all
from .document_loader import load_documents
from .embeddings import EmbeddingService
from .vector_store import VectorStore

logger = logging.getLogger("errorlens.ingestion")


def ingest_documents(
    vector_store: Optional[VectorStore] = None,
    force: bool = False,
    progress: bool = True,
) -> dict:
    """Run the full ingestion pipeline.

    Returns a summary dict: {loaded, chunks, written, language, took_s, skipped}.
    """
    settings = get_settings()
    start = time.perf_counter()
    store = vector_store or VectorStore()

    existing = store.count()
    if existing > 0 and not force:
        logger.info("Knowledge base already indexed (%d chunks) — skipping.", existing)
        return {
            "loaded": 0,
            "chunks": 0,
            "written": 0,
            "languages": [],
            "took_s": round(time.perf_counter() - start, 3),
            "skipped_reason": f"collection {settings.chroma_collection} already contains {existing} chunks",
        }

    documents = load_documents(settings.errors_dir)
    if not documents:
        raise ValueError(
            f"No Markdown documents found in {settings.errors_dir}. "
            "Add knowledge documents before running ingestion."
        )

    # We compute embeddings inside upsert_chunks if not provided, but to
    # report timing split it out explicitly.
    emb_service = EmbeddingService(settings.embedding_model)
    chunks = chunk_all(documents, max_chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    texts = [c.text for c in chunks]

    if progress:
        print(f"Ingesting {len(documents)} documents -> {len(chunks)} chunks "
              f"(model: {settings.embedding_model}) ...")
        t0 = time.perf_counter()

    embeddings = emb_service.embed_texts(texts)

    if progress:
        print(f"Embeddings computed in {time.perf_counter() - t0:.1f}s — writing to ChromaDB ...")

    store.upsert_chunks(chunks, embeddings)

    languages = sorted({d.language for d in documents})
    logger.info("Indexed %d chunks from %d documents in %.1fs", len(chunks), len(documents), time.perf_counter() - start)
    return {
        "loaded": len(documents),
        "chunks": len(chunks),
        "written": len(chunks),
        "languages": languages,
        "took_s": round(time.perf_counter() - start, 3),
        "skipped_reason": None,
    }


def ensure_indexed() -> dict:
    """Idempotent ingestion entrypoint used at application startup."""
    store = VectorStore()
    if store.count() > 0:
        return {"skipped": True, "count": store.count()}
    return ingest_documents(vector_store=store, force=False)