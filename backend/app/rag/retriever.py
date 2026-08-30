"""Semantic retrieval over the knowledge base using ChromaDB."""
from typing import List, Optional, Sequence

from app.config import get_settings

from .embeddings import EmbeddingService
from .vector_store import VectorStore


class RetrievedChunk:
    """A single retrieval result enriched with metadata and a relevance label."""

    def __init__(
        self,
        content: str,
        metadata: dict,
        similarity: float,
        distance: float,
    ) -> None:
        self.content = content
        self.metadata = metadata or {}
        self.similarity = similarity  # cosine similarity 0..1 (higher = closer)
        self.distance = distance      # chroma distance (lower = closer)

    @property
    def source_file(self) -> str:
        return self.metadata.get("source_file", "unknown.md")

    @property
    def error_name(self) -> str:
        return self.metadata.get("error_name", "")

    @property
    def language(self) -> str:
        return self.metadata.get("language", "")

    @property
    def section(self) -> str:
        return self.metadata.get("section", "")

    @property
    def relevance(self) -> str:
        """Coarse label derived from cosine similarity."""
        if self.similarity >= 0.55:
            return "High"
        if self.similarity >= 0.35:
            return "Medium"
        return "Low"

    def to_dict(self, max_content: int = 900) -> dict:
        return {
            "source_file": self.source_file,
            "error_name": self.error_name,
            "language": self.language,
            "section": self.section,
            "similarity": round(self.similarity, 4),
            "relevance": self.relevance,
            "content": self.content[:max_content],
        }


def cosine_from_distance(distance: float) -> float:
    """Chroma returns a cosine distance; convert back to similarity (clamp)."""
    return 1.0 - float(distance)


def _canonical_language(lang: Optional[str]) -> Optional[str]:
    """Map a possibly-lowercase language name to the casing used in metadata."""
    mapping = {
        "java": "Java",
        "python": "Python",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "sql": "SQL",
        "react": "React",
    }
    key = (lang or "").strip().lower()
    return mapping.get(key)


class Retriever:
    """Retrieve relevant knowledge chunks for a RAG query."""

    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ) -> None:
        settings = get_settings()
        self._store = vector_store or VectorStore(embedding_service=embedding_service)
        self._embeddings = embedding_service or self._store._embeddings
        self.top_k = settings.top_k

    def retrieve(
        self,
        query: str,
        top_k: int = 6,
        language_filter: Optional[str] = None,
        min_similarity: float = 0.0,
    ) -> List[RetrievedChunk]:
        """Embed the query and fetch the most relevant chunks.

        - De-duplicates by (source_file, section) so the same section appears once.
        - Prefers results from *different* sections/documents.
        """
        if not query.strip():
            return []

        query_embedding = self._embeddings.embed_query(query)

        where_filter = None
        canonical = _canonical_language(language_filter) if language_filter else None
        if canonical:
            where_filter = {"language": canonical}

        kwargs = {"n_results": max(top_k * 3, 24), "include": ["documents", "metadatas", "distances"]}
        if where_filter:
            kwargs["where"] = where_filter

        result = self._store.collection.query(
            query_embeddings=[query_embedding],
            **kwargs,
        )

        documents = (result.get("documents") or [[]])[0]
        metadatas = (result.get("metadatas") or [[]])[0]
        distances = (result.get("distances") or [[]])[0]

        seen: set = set()
        chunks: List[RetrievedChunk] = []
        for content, meta, distance in zip(documents, metadatas, distances):
            similarity = cosine_from_distance(distance)
            if similarity < min_similarity:
                continue
            ret_chunk = RetrievedChunk(content=content, metadata=meta, similarity=similarity, distance=distance)
            key = (ret_chunk.source_file, ret_chunk.section)
            if key in seen:
                continue
            seen.add(key)
            chunks.append(ret_chunk)
            if len(chunks) >= top_k:
                break
        return chunks

    def count(self) -> int:
        return self._store.count()