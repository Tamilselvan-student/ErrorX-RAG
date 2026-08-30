"""End-to-end test: user error → analysis → retrieval → context → LLM diagnosis.

This proves the RAG pipeline is real end-to-end (no hardcoded answers): the LLM
is mocked, but everything upstream (analyzer, query builder, ChromaDB retrieval
over the real knowledge documents, context builder) runs for real, and we assert
on what it produces.
"""
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.rag.chunker import chunk_document
from app.rag.document_loader import load_documents
from app.rag.retriever import Retriever

USER_ERROR = (
    'Exception in thread "main" java.lang.NullPointerException: '
    'Cannot invoke "User.getName()" because "user" is null\n'
    "\tat UserService.java:42\n"
)


def _seed_sample_knowledge(vector_store):
    docs = load_documents()
    chunks = []
    for doc in docs:
        if doc.filename in {
            "java_null_pointer_exception.md",
            "java_array_index_out_of_bounds.md",
            "python_key_error.md",
        }:
            chunks.extend(chunk_document(doc))
    vector_store.upsert_chunks(chunks)


def test_full_pipeline_user_error_to_diagnosis(vector_store, monkeypatch):
    _seed_sample_knowledge(vector_store)
    retriever = Retriever(vector_store=vector_store)

    # ---- Stage 1: analysis -------------------------------------------------
    from app.services.error_analyzer import analyze

    analysis = analyze(USER_ERROR, language_hint="auto")
    assert analysis.detected_error == "NullPointerException"
    assert analysis.language == "Java"

    # ---- Stage 2: query building -------------------------------------------
    from app.services.query_builder import build_rag_query

    rag_query = build_rag_query(analysis, USER_ERROR)
    assert "NullPointerException" in rag_query
    assert "Java" in rag_query or "java" in rag_query

    # ---- Stage 3: retrieval ------------------------------------------------
    chunks = retriever.retrieve(query=rag_query, top_k=5)
    assert chunks, "Expected at least one retrieved chunk"
    assert any(c.source_file == "java_null_pointer_exception.md" for c in chunks)
    assert len([c for c in chunks if c.source_file == "java_null_pointer_exception.md"]) >= 1

    # ---- Stage 4: context building ------------------------------------------
    from app.services.context_builder import build_context

    context = build_context(USER_ERROR, analysis, chunks)
    assert "ERROR INFORMATION:" in context
    assert "RETRIEVED KNOWLEDGE:" in context
    assert "java_null_pointer_exception.md" in context
    assert analysis.detected_error in context

    # ---- Stage 5: LLM (mocked) + diagnosis envelope -------------------------
    captured = {}

    def fake_llm(user_input, error_info, retrieved_context, model=None):
        captured["user_input"] = user_input
        captured["error_info"] = error_info
        captured["context"] = retrieved_context
        return "## Diagnosis\n\nGround truth from the supplied context.\n\n## How To Fix It\n\n1. Guard the null."

    monkeypatch.setattr(routes, "get_retriever", lambda: retriever)
    monkeypatch.setattr(routes.llm, "chat_completions", fake_llm)

    from app.main import create_app

    client = TestClient(create_app())
    resp = client.post("/api/analyze", json={"input": USER_ERROR, "language": "auto"})
    assert resp.status_code == 200
    body = resp.json()

    # The mocked LLM must have received the retrieved knowledge as context.
    assert "java_null_pointer_exception.md" in captured["context"]
    assert captured["error_info"]["detected_error"] == "NullPointerException"

    # The final diagnosis must flow through to the client with sources.
    assert "Ground truth from the supplied context." in body["diagnosis"]
    assert body["detected_error"] == "NullPointerException"
    assert body["confidence"] in ("High", "Medium", "Low")
    assert any(s["source_file"] == "java_null_pointer_exception.md" for s in body["sources"])


def test_context_builder_without_chunks_is_explicit(vector_store):
    """With no retrieval, the context says retrieval is empty (no fabrication)."""
    from app.services.context_builder import build_context
    from app.services.error_analyzer import analyze

    analysis = analyze("some totally unknown gibberish", language_hint="auto")
    context = build_context("some totally unknown gibberish", analysis, [])
    assert "(No knowledge chunks retrieved.)" in context