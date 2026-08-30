"""Tests for document loading and listing."""
from app.rag.document_loader import find_document, load_documents


def test_documents_loaded(errors_dir):
    docs = load_documents(errors_dir)
    assert len(docs) >= 25
    assert len(docs) <= 60


def test_frontmatter_is_parsed(errors_dir):
    docs = load_documents(errors_dir)
    for doc in docs:
        assert doc.error_name, f"{doc.filename} missing error_name"
        assert doc.language, f"{doc.filename} missing language"
        assert doc.category, f"{doc.filename} missing category"
        assert "## Description" in doc.content, f"{doc.filename} missing Description"


def test_language_coverage(errors_dir):
    docs = load_documents(errors_dir)
    languages = {d.language for d in docs}
    assert {"Java", "Python", "JavaScript", "SQL", "React"} <= languages


def test_required_sections_present(errors_dir):
    docs = load_documents(errors_dir)
    required = ["Description", "Common Causes", "Example", "Why It Happens",
                "Solutions", "Prevention", "Related Errors"]
    for doc in docs:
        missing = [s for s in required if "## " + s not in doc.content]
        assert not missing, f"{doc.filename} missing sections: {missing}"


def test_find_document_returns_content(errors_dir):
    content = find_document("java_null_pointer_exception.md", errors_dir)
    assert content is not None
    assert "NullPointerException" in content


def test_find_document_blocks_path_traversal(errors_dir):
    assert find_document("..\\..\\app\\config.py", errors_dir) is None
    assert find_document("../../app/config.py", errors_dir) is None
    assert find_document("not_there.md", errors_dir) is None