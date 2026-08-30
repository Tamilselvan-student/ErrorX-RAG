"""Chunk knowledge documents into meaningful, section-aware chunks.

Strategy
--------
1. Split the markdown body into sections at every ``## `` heading.
2. Keep each section as its own chunk (good semantic units for RAG).
3. If a section is too long, split it further into overlapping sub-chunks.
4. Attach the section name and source metadata to every chunk.
"""

CHUNK_SIZE = 600
CHUNK_OVERLAP = 60
import re
from dataclasses import dataclass, field
from typing import List, Optional

from .document_loader import RawDocument

_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)


@dataclass
class Chunk:
    """A single text chunk ready for embedding."""

    text: str
    section: str
    source_file: str
    error_name: str
    language: str
    category: str
    chunk_index: int = 0
    id: str = ""

    def build_id(self) -> str:
        """Deterministic id: source_file + section + first words + hash."""
        from hashlib import sha1

        seed = f"{self.source_file}|{self.section}|{self.chunk_index}|{self.text[:80]}"
        return f"{self.source_file}::{sha1(seed.encode('utf-8')).hexdigest()[:16]}"


def _split_long_text(text: str, max_len: int, overlap: int) -> List[str]:
    """Split a long block of text into overlapping pieces on sentence boundaries."""
    if len(text) <= max_len:
        return [text]
    pieces: List[str] = []
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    current = ""
    for sent in sentences:
        if len(current) + len(sent) + 1 > max_len and current:
            pieces.append(current.strip())
            keep = max(0, len(current) - overlap)
            current = (current[keep:] + " " if current[keep:] else "") + sent
        else:
            current = (current + " " if current else "") + sent
    if current and current.strip():
        pieces.append(current.strip())
    # Merge tiny leftovers to avoid useless fragments.
    merged: List[str] = []
    for piece in pieces:
        if piece:
            if merged and len(merged[-1]) + len(piece) <= max_len:
                merged[-1] = f"{merged[-1]} {piece}".strip()
            else:
                merged.append(piece)
    return merged or [text]


DEFAULT_SECTIONS = [
    "Description",
    "Common Causes",
    "Example",
    "Why It Happens",
    "Solutions",
    "Prevention",
    "Related Errors",
]

# Sections that are usually too useful to drop, even when tiny.
_KEEP_SECTIONS = {"Description", "Common Causes", "Why It Happens", "Solutions"}


def extract_sections(body: str) -> List[tuple[str, str]]:
    """Split a markdown body into (section, content) pairs.

    Uses ``## ``-level headings (the document template's section marker).
    ``# `` top-level titles are treated as part of the preamble, and any
    preamble text before the first section is attached to the first section
    that appears (or kept as 'Summary' if none exist).
    """
    matches = list(_HEADING_RE.finditer(body))
    if not matches:
        return [("Summary", body.strip())]

    sections: List[tuple[str, str]] = []
    preamble = body[: matches[0].start()].strip()
    for i, m in enumerate(matches):
        heading = m.group(0)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        text = body[start:end].strip()
        section_name = heading.strip().lstrip("#").strip()
        if i == 0 and preamble:
            text = f"{preamble}\n\n{text}".strip()
        sections.append((section_name, text))
    return sections


def chunk_document(
    document: RawDocument,
    max_chunk_size: int = 600,
    overlap: int = 60,
    min_chunk_size: int = 60,
    keep_sections: Optional[set] = None,
) -> List[Chunk]:
    """Produce chunks for a single document.

    Sections that are purely cross-reference lists (Related Errors) are
    usually useful context, so they are kept too — but the optional
    ``keep_sections`` filter lets callers drop noisy ones.
    """
    keep_sections = keep_sections or set(DEFAULT_SECTIONS)
    chunks: List[Chunk] = []
    for idx, (section, text) in enumerate(extract_sections(document.content)):
        if section not in keep_sections:
            continue
        if not text.strip():
            continue
        for j, piece in enumerate(_split_long_text(text, max_chunk_size, overlap)):
            if len(piece.strip()) < min_chunk_size and _split_long_text(text, max_chunk_size, overlap) == [text]:
                # tiny section — only keep it if it's genuinely informative
                if section not in _KEEP_SECTIONS:
                    continue
            chunk = Chunk(
                text=piece.strip(),
                section=section,
                source_file=document.filename,
                error_name=document.error_name,
                language=document.language,
                category=document.category,
                chunk_index=j,
            )
            chunk.id = chunk.build_id()
            chunks.append(chunk)
    return chunks


def chunk_all(
    documents: List[RawDocument],
    max_chunk_size: int = 600,
    overlap: int = 60,
) -> List[Chunk]:
    """Chunk a list of documents into one flat list."""
    chunks: List[Chunk] = []
    for doc in documents:
        chunks.extend(chunk_document(doc, max_chunk_size=max_chunk_size, overlap=overlap))
    return chunks