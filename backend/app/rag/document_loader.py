"""Load Markdown knowledge documents from the local error knowledge base.

Document format
---------------
Knowledge documents use YAML front matter:

    ---
    error_name: NullPointerException
    language: Java
    category: Runtime Error
    ---

    # NullPointerException

    ## Description
    ...

Required sections: Description, Common Causes, Example, Why It Happens,
Solutions, Prevention, Related Errors.
"""
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


@dataclass
class RawDocument:
    """A single parsed knowledge document."""

    filename: str
    error_name: str
    language: str
    category: str
    content: str  # full markdown body (front matter stripped)


def _parse_frontmatter(text: str) -> Dict[str, str]:
    """Parse simple YAML key: value front matter into a dict."""
    metadata: Dict[str, str] = {}
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return metadata
    block = match.group(1)
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            metadata[key.strip()] = value.strip()
    return metadata


def split_frontmatter(text: str):
    """Return (metadata_dict, body_without_frontmatter)."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    body = text[match.end():].lstrip("\n")
    return _parse_frontmatter(text), body


def load_documents(errors_dir: Optional[Path] = None) -> List[RawDocument]:
    """Read every *.md file under errors_dir and parse subtitle/front matter."""
    errors_dir = errors_dir or Path(__file__).resolve().parent.parent.parent / "data" / "errors"
    if not errors_dir.exists():
        raise FileNotFoundError(f"Knowledge base directory not found: {errors_dir}")

    documents: List[RawDocument] = []
    for path in sorted(errors_dir.glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        metadata, body = split_frontmatter(raw)

        error_name = metadata.get("error_name", "").strip() or path.stem.replace("_", " ").title()
        docs = RawDocument(
            filename=path.name,
            error_name=error_name,
            language=metadata.get("language", "Unknown").strip() or "Unknown",
            category=metadata.get("category", "General").strip() or "General",
            content=body.strip(),
        )
        documents.append(docs)
    return documents


def find_document(filename: str, errors_dir: Optional[Path] = None) -> Optional[str]:
    """Return the full raw markdown content of a knowledge document, or None.

    The filename is sanitized (basename only) to avoid path traversal.
    """
    errors_dir = errors_dir or Path(__file__).resolve().parent.parent.parent / "data" / "errors"
    safe_name = Path(filename).name  # strips any directory traversal
    path = errors_dir / safe_name
    if not path.exists() or not path.is_file() or path.suffix != ".md":
        return None
    return path.read_text(encoding="utf-8")