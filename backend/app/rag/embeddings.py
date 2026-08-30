"""Embedding wrapper around sentence-transformers.

The model is loaded lazily and cached for the process lifetime so it is only
downloaded/loaded once, which keeps startup fast.
"""
from typing import List, Optional

from app.config import get_settings


class EmbeddingService:
    """Thin wrapper around a sentence-transformers model."""

    def __init__(self, model_name: Optional[str] = None) -> None:
        settings = get_settings()
        self.model_name = model_name or settings.embedding_model
        self._model = None

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of texts into a list of float vectors."""
        if not texts:
            return []
        vectors = self.model.encode(
            [str(t) for t in texts],
            normalize_embeddings=True,
            batch_size=32,
            show_progress_bar=False,
        )
        return [list(map(float, v)) for v in vectors]

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        return self.embed_texts([text])[0]

    @property
    def dimension(self) -> int:
        return self.model.get_sentence_embedding_dimension()