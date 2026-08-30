"""API tests using FastAPI TestClient.

The heavy sentence-transformers model is never loaded: the retriever is replaced
with one backed by the fake embeddings + a temp ChromaDB, and the LLM call is
mocked.
"""
import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.rag.chunker import chunk_document
from app.rag.document_loader import load_documents
from app.rag.retriever import Retriever


FAKE_DIAGNOSIS = """## Diagnosis

The error is a NullPointerException.

## What This Error Means

It means code dereferenced a null reference.

## Likely Root Cause

- **Likely** calling a method on a null user.

## How To Fix It

1. Null-check the user.

## Example

if (user == null) { return; }

## How To Prevent It

- Add guards.

## Related Errors

- ClassCastException
"""


@pytest.fixture
def client(vector_store, monkeypatch):
    """TestClient whose retriever points at a temp store and LLM is mocked."""
    docs = load_documents()
    chunks = []
    for doc in docs:
        if doc.filename in {
            "java_null_pointer_exception.md",
            "python_key_error.md",
            "javascript_type_error.md",
        }:
            chunks.extend(chunk_document(doc))
    vector_store.upsert_chunks(chunks)

    retriever = Retriever(vector_store=vector_store)
    monkeypatch.setattr(routes, "get_retriever", lambda: retriever)

    def fake_llm(*args, **kwargs):
        return FAKE_DIAGNOSIS

    monkeypatch.setattr(routes.llm, "chat_completions", fake_llm)

    from app.main import create_app

    return TestClient(create_app())


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "llm_configured" in body
    assert "documents_indexed" in body


def test_analyze_returns_structured_response(client):
    resp = client.post(
        "/api/analyze",
        json={"input": "java.lang.NullPointerException at UserService.java:42", "language": "auto"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["detected_error"] == "NullPointerException"
    assert body["language"] == "Java"
    assert body["confidence"] in ("High", "Medium", "Low")
    assert "Diagnosis" in body["diagnosis"]
    assert body["sources"], "Expected retrieved sources"
    assert any(s["source_file"] == "java_null_pointer_exception.md" for s in body["sources"])
    assert body["rag_query"]


def test_analyze_returns_sources_with_metadata(client):
    resp = client.post("/api/analyze", json={"input": "KeyError: 'settings'", "language": "auto"})
    assert resp.status_code == 200
    body = resp.json()
    for src in body["sources"]:
        assert {"source_file", "error_name", "language", "section", "similarity", "relevance"} <= set(src)


def test_analyze_empty_input_rejected(client):
    resp = client.post("/api/analyze", json={"input": "   ", "language": "auto"})
    assert resp.status_code == 422


def test_analyze_unknown_error_still_works(client):
    resp = client.post("/api/analyze", json={"input": "Something exploded", "language": "auto"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["confidence"] in ("High", "Medium", "Low")


def test_analyze_unsupported_language_rejected(client):
    resp = client.post("/api/analyze", json={"input": "x", "language": "rust"})
    assert resp.status_code == 422


def test_analyze_missing_llm_returns_friendly_503(client, monkeypatch):
    def boom(*args, **kwargs):
        raise routes.llm.LLMNotConfiguredError("no key")

    monkeypatch.setattr(routes.llm, "chat_completions", boom)
    resp = client.post("/api/analyze", json={"input": "NullPointerException at line 1"})
    assert resp.status_code == 503
    assert "LLM_API_KEY" in resp.json()["detail"]


def test_search_works_without_llm(client):
    resp = client.post("/api/search", json={"input": "NullPointerException", "language": "auto"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["detected_error"] == "NullPointerException"
    assert body["results"]


def test_examples_endpoint(client):
    resp = client.get("/api/examples")
    assert resp.status_code == 200
    examples = resp.json()
    assert len(examples) >= 4
    for ex in examples:
        assert ex["title"] and ex["input"] and ex["language"]


def test_documents_endpoint(client):
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    names = resp.json()
    assert "java_null_pointer_exception.md" in names


def test_document_detail_and_traversal_guard(client):
    ok = client.get("/api/documents/java_null_pointer_exception.md")
    assert ok.status_code == 200
    assert "NullPointerException" in ok.json()["content"]

    bad = client.get("/api/documents/..%2F..%2Fapp%2Fconfig.py")
    assert bad.status_code == 404