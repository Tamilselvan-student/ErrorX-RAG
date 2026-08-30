"""API routes for ErrorLens."""
import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app import models
from app.rag.document_loader import find_document
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore
from app.services import llm
from app.services.confidence import compute_confidence
from app.services.context_builder import build_context
from app.services.error_analyzer import AnalysisResult, analyze
from app.services.examples import get_examples
from app.services.query_builder import build_rag_query

logger = logging.getLogger("errorlens.api")

router = APIRouter(prefix="/api")

# Module-level singleton (kept for the server process lifetime).
_retriever: "Retriever | None" = None


def get_retriever() -> Retriever:
    global _retriever
    if _retriever is None:
        _retriever = Retriever()
    return _retriever


def _run_pipeline(payload: models.AnalyzeRequest) -> tuple:
    """Analyze -> build query -> retrieve. Returns (analysis, rag_query, chunks)."""
    retriever = get_retriever()
    analysis: AnalysisResult = analyze(payload.input, language_hint=payload.language)

    rag_query = build_rag_query(analysis, payload.input)

    # Only narrow by language when the user forced one AND it resolved.
    lang_filter = None
    if payload.language.strip().lower() not in ("", "auto"):
        lang_filter = analysis.language if analysis.language else None

    chunks = retriever.retrieve(
        query=rag_query,
        top_k=payload.top_k,
        language_filter=lang_filter,
    )
    return analysis, rag_query, chunks


@router.get("/health", response_model=models.HealthResponse, tags=["system"])
def health():
    from app import __version__
    from app.config import get_settings

    settings = get_settings()
    store = VectorStore()
    return models.HealthResponse(
        status="ok",
        message="ErrorLens backend is running.",
        llm_configured=settings.llm_configured,
        llm_model=settings.llm_model,
        embedding_model=settings.embedding_model,
        documents_indexed=store.count(),
        collection=settings.chroma_collection,
        app_version=__version__,
    )


@router.post("/analyze", response_model=models.AnalyzeResponse, tags=["rag"])
def analyze_endpoint(payload: models.AnalyzeRequest):
    analysis, rag_query, chunks = _run_pipeline(payload)

    if not chunks:
        raise HTTPException(
            status_code=503,
            detail=(
                "No relevant knowledge was retrieved from the knowledge base. "
                "The error index may be empty — try running the ingestion "
                "pipeline (POST /api/index) first."
            ),
        )
    return _build_analyze_response(payload, analysis, rag_query, chunks)


def _build_analyze_response(payload: models.AnalyzeRequest, analysis: AnalysisResult,
                            rag_query: str, chunks) -> models.AnalyzeResponse:
    """Assemble context, confidence, LLM output, and the response envelope."""
    context = build_context(payload.input, analysis, chunks)
    confidence = compute_confidence(analysis, chunks)

    warnings: List[str] = []
    if confidence.level == "Low":
        warnings.append(
            "Confidence is low — provide the full stack trace or surrounding "
            "code for a more reliable diagnosis."
        )
    if not analysis.language:
        warnings.append(
            "Language could not be confidently detected. Select a language "
            "explicitly for better results."
        )

    sources = [c.to_dict() for c in chunks]

    # The LLM is contacted after retrieval; if not configured we surface a
    # friendly, explicit error instead of fabricating a diagnosis.
    try:
        diagnosis = llm.chat_completions(
            user_input=payload.input,
            error_info={
                "language": analysis.language,
                "detected_error": analysis.detected_error,
                "error_type": analysis.error_type,
                "category": analysis.category,
            },
            retrieved_context=context,
        )
    except llm.LLMNotConfiguredError as exc:
        logger.warning("LLM not configured: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=(
                "LLM is not configured yet. Add LLM_API_KEY (and optionally "
                "LLM_BASE_URL, LLM_MODEL) to your .env file, then restart the "
                "backend. Retrieval works — use POST /api/search to inspect "
                "the retrieved knowledge."
            ),
        ) from exc
    except llm.LLMError as exc:
        logger.error("LLM failure: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=(
                "The LLM request failed. Check your LLM_BASE_URL / LLM_MODEL "
                "configuration and your network connection."
            ),
        ) from exc

    return models.AnalyzeResponse(
        detected_error=analysis.detected_error or "Unknown",
        language=analysis.language or "Unknown",
        language_confidence=analysis.language_confidence,
        category=analysis.category or "Unknown",
        error_type=analysis.error_type,
        confidence=confidence.level,
        confidence_reason=confidence.reason,
        diagnosis=diagnosis,
        sources=sources,
        keywords=analysis.keywords,
        rag_query=rag_query,
        warnings=warnings,
    )
@router.post("/search", response_model=models.SearchResponse, tags=["rag"])
def search_endpoint(payload: models.SearchRequest):
    plain = models.AnalyzeRequest(input=payload.input, language=payload.language)
    analysis, rag_query, chunks = _run_pipeline(plain)
    results = [c.to_dict() for c in chunks]
    return models.SearchResponse(
        detected_error=analysis.detected_error or "Unknown",
        language=analysis.language or "Unknown",
        category=analysis.category or "Unknown",
        keywords=analysis.keywords,
        rag_query=rag_query,
        results=results,
    )


@router.post("/index", response_model=dict, tags=["rag"])
def index_endpoint(force: bool = Query(False, description="Force re-indexing")):
    from app.rag.ingestion import ingest_documents

    try:
        summary = ingest_documents(force=force)
        return {"status": "ok", **summary}
    except Exception as exc:
        logger.exception("Ingestion failed")
        raise HTTPException(500, f"Ingestion failed: {exc}") from exc


@router.get("/examples", response_model=List[dict], tags=["rag"])
def examples_endpoint():
    return get_examples()


@router.get("/documents", response_model=List[str], tags=["knowledge"])
def list_documents():
    from app.rag.document_loader import load_documents

    docs = load_documents()
    return sorted(doc.filename for doc in docs)


@router.get("/documents/{filename}", response_model=models.DocumentInfo, tags=["knowledge"])
def get_document(filename: str):
    content = find_document(filename)
    if content is None:
        raise HTTPException(404, f"Document '{filename}' was not found in the knowledge base.")
    return models.DocumentInfo(filename=filename, content=content)