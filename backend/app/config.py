"""Application configuration loaded from environment variables.

Never hardcode API keys in source code — everything sensitive comes from the
environment (see the project root .env.example).
"""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Root directory of the backend package (backend/)
BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Load .env files: project root first (recommended), then backend/.env.
for _candidate in (PROJECT_ROOT / ".env", BACKEND_DIR / ".env"):
    if _candidate.exists():
        load_dotenv(_candidate)

# Absolute paths used by the RAG pipeline.
ERRORS_DIR = BACKEND_DIR / "data" / "errors"
CHROMA_DIR = BACKEND_DIR / "chroma_db"
CHROMA_COLLECTION = "errorlens_errors"

# Ingestion objects to use for a while.
CHUNK_SIZE = 600
CHUNK_OVERLAP = 60


class Settings:
    """Read-only settings bag. Values are read from env at construction time."""

    def __init__(self) -> None:
        self.project_root: Path = PROJECT_ROOT
        self.backend_dir: Path = BACKEND_DIR
        self.errors_dir: Path = ERRORS_DIR
        self.chroma_dir: Path = CHROMA_DIR
        self.chroma_collection: str = CHROMA_COLLECTION

        # Embedding model (sentence-transformers). Downloaded on first use.
        self.embedding_model: str = os.environ.get(
            "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
        )

        # OpenAI-compatible LLM configuration.
        self.llm_api_key: str = os.environ.get("LLM_API_KEY", "").strip()
        self.llm_base_url: str = os.environ.get("LLM_BASE_URL", "").strip() or None
        self.llm_model: str = os.environ.get("LLM_MODEL", "").strip() or "gpt-4o-mini"
        self.llm_temperature: float = float(os.environ.get("LLM_TEMPERATURE", "0.2"))
        self.llm_timeout: float = float(os.environ.get("LLM_TIMEOUT", "120"))

        # Retrieval knobs.
        self.top_k: int = int(os.environ.get("ERRORLENS_TOP_K", "6"))
        self.default_language: str = "auto"

        # UI/UX knobs.
        self.api_port: int = int(os.environ.get("ERRORLENS_PORT", "8000"))
        self.api_host: str = os.environ.get("ERRORLENS_HOST", "0.0.0.0")

    @property
    def llm_configured(self) -> bool:
        """Whether an API key (or at least a non-default base URL) is available."""
        return bool(self.llm_api_key) or bool(self.llm_base_url)

    def as_dict(self) -> dict:
        """Public, non-secret status snapshot. Never includes keys."""
        return {
            "embedding_model": self.embedding_model,
            "llm_model": self.llm_model,
            "llm_base_url": self.llm_base_url or "(default)",
            "llm_configured": self.llm_configured,
            "top_k": self.top_k,
            "collection": self.chroma_collection,
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor (singleton per process)."""
    return Settings()