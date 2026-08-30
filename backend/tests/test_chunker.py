"""Tests for section-based markdown chunking."""
from app.rag.chunker import chunk_document
from app.rag.document_loader import load_documents


def _doc_by_name(errors_dir, name):
    return next(d for d in load_documents(errors_dir) if d.filename == name)


def test_chunking_produces_section_metadata(errors_dir):
    doc = _doc_by_name(errors_dir, "java_null_pointer_exception.md")
    chunks = chunk_document(doc)
    assert len(chunks) >= 5  # at least one chunk per meaningful section

    expected_sections = {"Description", "Common Causes", "Example", "Why It Happens", "Solutions", "Prevention", "Related Errors"}
    for chunk in chunks:
        assert chunk.section in expected_sections
        assert chunk.source_file == doc.filename
        assert chunk.error_name == "NullPointerException"
        assert chunk.language == "Java"
        assert chunk.category == doc.category
        assert chunk.text.strip()


def test_chunk_ids_are_unique(errors_dir):
    docs = load_documents(errors_dir)
    ids = []
    for doc in docs[:8]:
        ids += [c.id for c in chunk_document(doc)]
    assert len(ids) == len(set(ids))


def test_long_sections_are_split(errors_dir):
    doc = _doc_by_name(errors_dir, "python_import_error.md")
    chunks = [c for c in chunk_document(doc) if c.section == "Common Causes"]
    assert chunks
    for chunk in chunks:
        assert len(chunk.text) <= 1500


def test_all_docs_chunkable(errors_dir):
    docs = load_documents(errors_dir)
    total = 0
    for doc in docs:
        total += len(chunk_document(doc))
    assert total > 100