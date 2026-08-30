"""Pydantic models for the ErrorLens API requests/responses."""

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

# Languages the knowledge base understands.
SUPPORTED_LANGUAGES = ["java", "python", "javascript", "sql", "react"]


class AnalyzeRequest(BaseModel):
    """Payload for POST /api/analyze."""

    input: str = Field(..., min_length=1, description="User input: error message, stack trace, or code snippet.")
    language: str = Field(
        "auto",
        description="Language hint. One of: auto, java, python, javascript, sql, react.",
    )
    top_k: int = Field(6, ge=1, le=20, description="Number of knowledge chunks to retrieve.")

    @field_validator("input")
    @classmethod
    def validate_input(cls, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValueError("Input must contain at least one non-whitespace character.")
        return value

    @field_validator("language", "top_k", mode="before")
    @classmethod
    def normalize_language(cls, value):
        if isinstance(value, str):
            lang = value.strip().lower()
            if lang and lang != "auto" and lang not in SUPPORTED_LANGUAGES:
                raise ValueError(
                    f"Unsupported language '{value}'. Choose from: auto, {', '.join(SUPPORTED_LANGUAGES)}."
                )
            return lang
        return value


class SearchRequest(BaseModel):
    """Payload for POST /api/search (retrieval-only, no LLM)."""

    input: str = Field(..., min_length=1)
    language: str = Field("auto")


class IndexRequest(BaseModel):
    """Payload for POST /api/index."""

    force: bool = Field(False, description="Re-index even if data already exists.")


class SourceDocument(BaseModel):
    """A knowledge chunk retrieved for a diagnosis."""

    source_file: str
    error_name: str
    language: str
    section: str
    similarity: float
    relevance: str = Field(description="High / Medium / Low, derived from similarity.")
    content: str = Field(description="Truncated chunk preview shown in the UI.")


class AnalyzeResponse(BaseModel):
    """Response for POST /api/analyze."""

    detected_error: str
    language: str
    language_confidence: Optional[str] = None
    category: str
    error_type: str
    confidence: str  # High / Medium / Low
    confidence_reason: str
    diagnosis: str  # Markdown produced by the LLM
    sources: List[SourceDocument] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    rag_query: str
    warnings: List[str] = Field(default_factory=list)


class SearchResponse(BaseModel):
    """Response for POST /api/search."""

    detected_error: str
    language: str
    category: str
    keywords: List[str]
    rag_query: str
    results: List[SourceDocument] = Field(default_factory=list)


class DocumentInfo(BaseModel):
    """Envelope for serving a knowledge document."""

    filename: str
    content: str


class HealthResponse(BaseModel):
    status: str
    message: str
    llm_configured: bool
    llm_model: str
    embedding_model: str
    documents_indexed: Optional[int] = None
    collection: str
    app_version: str