"""Persistent ChromaDB vector store for error knowledge chunks."""
from typing import Dict, List, Optional

from app.config import get_settings

from .chunker import Chunk
from .embeddings import EmbeddingService


class VectorStore:
    """Owns the ChromaDB collection. Persists to disk under backend/chroma_db."""

    def __init__(
        self,
        embedding_service: Optional[EmbeddingService] = None,
        collection_name: Optional[str] = None,
        persist_dir: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self._embeddings = embedding_service or EmbeddingService()
        self._collection_name = collection_name or settings.chroma_collection
        self._persist_dir = persist_dir or str(settings.chroma_dir)
        self._collection = None
        self._client = None

    @property
    def client(self):
        """Lazily build the persistent ChromaDB client."""
        if self._client is None:
            import chromadb

            # ``chromadb.PersistentClient`` stores data on disk. ``get_or_create_collection``
            # keeps the same collection between restarts (persistent — does NOT regenerate).
            self._client = chromadb.PersistentClient(path=self._persist_dir)
        return self._client

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name=self._collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def count(self) -> int:
        try:
            return self.collection.count()
        except Exception:
            return 0

    def snapshot(self) -> dict:
        return {
            "collection": self._collection_name,
            "persist_dir": self._persist_dir,
            "count": self.count(),
        }

    def upsert_chunks(
        self, chunks: List[Chunk], embeddings: Optional[List[List[float]]] = None
    ) -> int:
        """Insert (or replace) chunks and their embeddings.

        Returns the number of chunks written.
        """
        if not chunks:
            return 0
        if embeddings is None:
            embeddings = self._embeddings.embed_texts([c.text for c in chunks])

        self.collection.upsert(
            ids=[c.id for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=embeddings,
            metadatas=[c_meta(c) for c in chunks],
        )
        return len(chunks)


def c_meta(chunk: Chunk) -> Dict[str, str]:
    """Metadata stored for every vector — exactly matches the RAG metadata spec."""
    return {
        "error_name": chunk.error_name,
        "language": chunk.language,
        "category": chunk.category,
        "source_file": chunk.source_file,
        "section": chunk.section,
    }