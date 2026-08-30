"""Development launcher for the ErrorLens backend.

Loads environment variables from the .env file (if present) and starts the
FastAPI application with uvicorn on http://localhost:8000.

Usage:
    python run.py
"""
import os

from dotenv import load_dotenv

# Load environment variables from the project root .env, then from backend/.env
# (relative to this file's location), whichever exists first.
_ENV_CANDIDATES = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
    os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
]
for candidate in _ENV_CANDIDATES:
    if os.path.exists(candidate):
        load_dotenv(candidate)
        break

if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("ERRORLENS_PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host=os.environ.get("ERRORLENS_HOST", "0.0.0.0"),
        port=port,
        reload=True,
    )