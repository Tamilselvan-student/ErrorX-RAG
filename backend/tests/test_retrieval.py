"""Tests for ChromaDB-backed semantic retrieval."""
from app.rag.chunker import chunk_document
from app.rag.document_loader import load_documents


def _seed(vector_store, names):
    docs = load_documents()
    chunks = []
    for doc in docs:
        if doc.filename in names:
            chunks.extend(chunk_document(doc))
    vector_store.upsert_chunks(chunks)
    return chunks


def test_retrieval_finds_relevant_document(retriever, vector_store):
    _seed(vector_store, ["java_null_pointer_exception.md", "python_key_error.md"])
    results = retriever.retrieve(
        "Java NullPointerException user getName null dereference", top_k=4
    )
    assert results
    assert any("java_null_pointer_exception.md" == r.source_file for r in results)
    for r in results:
        assert 0.0 <= r.similarity <= 1.0
        assert r.relevance in ("High", "Medium", "Low")


def test_retrieval_deduplicates_sections(retriever, vector_store):
    _seed(vector_store, ["java_null_pointer_exception.md"])
    results = retriever.retrieve(
        "NullPointerException common causes solutions prevent", top_k=10
    )
    keys = [(r.source_file, r.section) for r in results]
    assert len(keys) == len(set(keys))


def test_retrieval_respects_language_filter(retriever, vector_store):
    _seed(vector_store, ["java_null_pointer_exception.md", "python_key_error.md"])
    results = retriever.retrieve("exception", top_k=10, language_filter="python")
    assert results
    assert all(r.language == "Python" for r in results)


def test_retrieval_empty_query_returns_nothing(retriever):
    assert retriever.retrieve("   ") == []


def test_top_k_respected(retriever, vector_store):
    chunks = _seed(vector_store, ["java_null_pointer_exception.md"])
    assert len(chunks) > 6
    results = retriever.retrieve("null pointer", top_k=4)
    assert len(results) <= 4