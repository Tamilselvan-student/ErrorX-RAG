"""Shared test fixtures.

Tests avoid loading the real (heavy) sentence-transformers model by using a
deterministic fake embedding service backed by a temporary ChromaDB directory.
"""
import math
import re
import tempfile
from pathlib import Path

import pytest

from app.config import get_settings


class FakeEmbeddings:
    """Deterministic bag-of-token hashing embeddings (no model download)."""

    DIM = 128

    def __init__(self, model_name="fake-mini"):
        self.model_name = model_name

    def _vector(self, text: str):
        vec = [0.0] * self.DIM
        for token in re.findall(r"[a-z0-9_]+", str(text).lower()):
            h = hash(token) & 0xFFFFFFFF
            vec[h % self.DIM] += 1.0
        norm = math.sqrt(sum(v * v for v in vec))
        if norm == 0:
            return vec
        return [v / norm for v in vec]

    def embed_texts(self, texts):
        return [self._vector(t) for t in texts]

    def embed_query(self, text):
        return self._vector(text)


@pytest.fixture
def fake_embeddings():
    return FakeEmbeddings()


@pytest.fixture
def errors_dir():
    return get_settings().errors_dir


@pytest.fixture
def temp_chroma_dir():
    """A scratch dir for ChromaDB, with Windows-tolerant cleanup.

    ChromaDB can hold file handles briefly after a test; plain
    TemporaryDirectory cleanup occasionally raises NotADirectoryError on
    Windows, so we retry rmtree a few times and ignore residual errors.
    """
    import shutil
    import tempfile
    import time

    path = tempfile.mkdtemp(prefix="errorlens-test-")
    yield path
    for _ in range(6):
        try:
            shutil.rmtree(path)
            return
        except OSError:
            time.sleep(0.5)
    shutil.rmtree(path, ignore_errors=True)


@pytest.fixture
def vector_store(fake_embeddings, temp_chroma_dir):
    """A VectorStore on a temp dir using fake embeddings."""
    from app.rag.vector_store import VectorStore

    return VectorStore(
        embedding_service=fake_embeddings,
        collection_name="test_errors",
        persist_dir=temp_chroma_dir,
    )


@pytest.fixture
def retriever(vector_store):
    from app.rag.retriever import Retriever

    return Retriever(vector_store=vector_store)