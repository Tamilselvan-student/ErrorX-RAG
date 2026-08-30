"""FastAPI application entrypoint for ErrorLens.

Startup behaviour
-----------------
* On process start, ingests the knowledge base *only if the ChromaDB
  collection is empty* (the persisted DB is reused otherwise — see
  ``app.rag.ingestion.ensure_indexed``).
* If ingestion fails (e.g. embedded model download blocked, no network) the
  app still boots so the health endpoint and other routes respond.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.routes import router
from app.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("errorlens")

APP_STATE = {"indexed": False, "index_error": None}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Non-blocking startup ingestion (best-effort).
    try:
        from app.rag.ingestion import ensure_indexed

        result = ensure_indexed()
        APP_STATE["indexed"] = result.get("skipped", False) or result.get("chunks", 0) > 0
        logger.info("Knowledge base ready: %s", result)
    except Exception as exc:  # pragma: no cover - depends on external downloads
        APP_STATE["index_error"] = str(exc)
        logger.error("Knowledge base ingestion failed at startup: %s", exc)
    yield
    logger.info("Shutting down ErrorLens backend.")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ErrorLens API",
        description="AI Error Diagnosis & Explanation Assistant (RAG).",
        version=__version__,
        lifespan=lifespan,
    )

    # Development CORS: the Vite dev server runs on a different port.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router)

    # --- Friendly error handling ---------------------------------------------
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        # Extract the first human-readable violation.
        detail = "Invalid request."
        if exc.errors():
            first = exc.errors()[0]
            loc = ".".join(str(p) for p in first.get("loc", []) if p != "body")
            msg = first.get("msg", "")
            detail = f"{loc}: {msg}" if loc else msg
        return JSONResponse(status_code=422, content={"detail": detail})

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error for %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again later."},
        )

    @app.get("/", include_in_schema=False)
    def root():
        return {
            "app": "ErrorLens",
            "version": __version__,
            "docs": "/docs",
            "health": "/api/health",
        }

    return app


app = create_app()