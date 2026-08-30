"""Assemble the RAG context handed to the LLM.

The context block is designed to make provenance obvious: every chunk shows its
source document, error name, language, section, and relevance.
"""
from typing import List, Optional

from app.rag.retriever import RetrievedChunk

from .error_analyzer import AnalysisResult


def _render_chunk(c: RetrievedChunk) -> str:
    relevance = c.relevance
    lines = [
        f"Source: {c.source_file}",
        f"Error: {c.error_name or '—'}",
        f"Language: {c.language or '—'}",
        f"Section: {c.section or '—'}",
        f"Relevance: {relevance}",
        "---",
        c.content,
    ]
    return "\n".join(lines)


def build_context(
    user_input: str,
    analysis: AnalysisResult,
    chunks: List[RetrievedChunk],
    max_chunk_chars: int = 1200,
) -> str:
    """Build the context block passed to the LLM as factual reference material."""
    rendered_chunks = []
    for chunk in chunks:
        if chunk.content:
            rendered = _render_chunk(chunk)
            rendered_chunks.append(rendered[: max_chunk_chars * 2])

    header = (
        "ERROR INFORMATION:\n\n"
        f"Language: {analysis.language or 'Unknown'}\n"
        f"Detected Error: {analysis.detected_error or 'Not identified'}\n"
        f"Category: {analysis.category or 'Not identified'}\n"
        f"User Input:\n{user_input.strip()}\n\n"
    )

    if not rendered_chunks:
        return header + "RETRIEVED KNOWLEDGE:\n\n(No knowledge chunks retrieved.)\n"

    knowledge = "RETRIEVED KNOWLEDGE:\n\n" + "\n\n---\n\n".join(rendered_chunks) + "\n"
    return header + knowledge