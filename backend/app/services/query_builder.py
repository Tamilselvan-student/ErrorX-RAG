"""Build the RAG query from an analyzed error.

Converts the structured analysis into a concise, embedding-friendly query string
in the style: "Java NullPointerException User getName null object causes fixes".
"""
from typing import List

from .error_analyzer import AnalysisResult

# Words that help the retriever find cause/solution sections but pollute a query.
_QUERY_NOISE = {"user", "input"}


def build_rag_query(
    analysis: AnalysisResult,
    original_text: str,
    max_tokens: int = 40,
) -> str:
    """Compose the semantic query used for ChromaDB retrieval."""
    parts: List[str] = []

    if analysis.language and analysis.language.lower() not in ("unknown", ""):
        parts.append(analysis.language)

    if analysis.detected_error:
        parts.append(analysis.detected_error)

    # Add meaningful analysis keywords first.
    for keyword in analysis.keywords:
        if keyword.lower() not in _QUERY_NOISE and len(parts) < 6:
            parts.append(keyword)

    # Add stack-trace file names (minus extension) verbatim — very specific.
    seen_files: set = set()
    for frame in analysis.stack_frames:
        fname = frame.get("file", "").split("\\")[-1].split("/")[-1]
        stem = fname.rsplit(".", 1)[0] if "." in fname else fname
        if stem and stem.lower() not in seen_files and stem.lower() not in _QUERY_NOISE:
            seen_files.add(stem.lower())
            if len(parts) < 9:
                parts.append(stem)

    # If nothing else survived, fall back to trimmed raw text.
    if len(parts) < 3 and original_text.strip():
        raw = " ".join(original_text.split())[:120]
        parts.append(raw)

    query = " ".join(parts)
    return query[: max_tokens * 8]