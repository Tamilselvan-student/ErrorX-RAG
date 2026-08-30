# ErrorLens — AI Error Diagnosis & Explanation Assistant

ErrorLens is a **RAG-powered** application that helps developers understand
programming errors. Paste an error message, a stack trace, or a short piece of
problematic code — ErrorLens analyzes it, retrieves relevant explanations from a
**local error knowledge base** via vector search, and produces a structured,
source-cited diagnosis with an LLM.

```
NullPointerException at UserService.java:42      → full structured diagnosis
TypeError: Cannot read properties of undefined   → cause + fix + prevention
SELECT * FROM users WHERE id = NULL;             → silent-logic-bug explanation
```

Everything is **real**: no hardcoded answers, no fake RAG. Every claim in the
diagnosis is grounded in retrieved knowledge documents shown to the user.

---

## Problem Statement

Developers waste significant time deciphering cryptic runtime errors. Errors
like `NullPointerException`, `KeyError`, `TypeError`, SQL constraint failures,
or React hook violations all have *well-known* causes and fixes — but that
knowledge lives scattered across docs, Stack Overflow, and years of experience.

ErrorLens closes the loop locally:

1. **Analyze** the raw error deterministically (language, error type, keywords).
2. **Retrieve** the most relevant explanations from a curated local knowledge
   base using embeddings + ChromaDB (Retrieval-Augmented Generation).
3. **Diagnose** with an LLM *required* to base every claim on the retrieved
   knowledge and to distinguish likely from confirmed causes.
4. **Cite** the exact source documents used, so every claim can be verified.

---

## Features

- 🧠 **Real RAG pipeline** — sentence-transformers embeddings → ChromaDB semantic
  search → context assembly → grounded LLM diagnosis.
- 🔍 **Deterministic error analyzer** — language, error type, category, keywords,
  and stack-trace locations via simple reliable pattern matching.
- 📚 **Local knowledge base** — 36 hand-written Markdown documents covering Java,
  Python, JavaScript, SQL, and React (Description / Common Causes / Example /
  Why It Happens / Solutions / Prevention / Related Errors).
- 💾 **Persistent vector store** — documents embedded once; the ChromaDB store
  persists across restarts and is never rebuilt while non-empty.
- 🎯 **Confidence indicator** — transparent High / Medium / Low labels from
  language detection, error detection, retrieval relevance, and keyword overlap
  (deliberately *not* a calibrated probability).
- 📄 **Source citations** — the UI shows every knowledge document used; click a
  source to open the full Markdown document.
- 🧪 **Example mode** — one-click realistic errors, all through the real pipeline.
- 🛡️ **Security-minded** — user input never executed, no shell commands, no key
  exposure, sanitized file serving, friendly error messages only.

---

## Architecture

```
┌─────────────┐     ┌──────────────────────────────────────────────┐
│   React UI  │     │              FastAPI backend                 │
│  (Vite +    │◄───►│                                              │
│  Tailwind)  │ /api│  ┌───────────┐ ┌─────────┐ ┌──────────────┐  │
└─────────────┘     │  │  ERROR    │ │ QUERY   │ │   EMBEDDING  │  │
                    │  │ ANALYZER  │►│ BUILDER │►│    MODEL     │  │
                    │  └───────────┘ └─────────┘ └──────┬───────┘  │
                    │                                   ▼         │
                    │                        ┌──────────────────┐ │
                    │                        │    CHROMADB      │ │
                    │                        │  vector store    │ │
                    │                        └───────┬──────────┘ │
                    │   ┌────────────┐ ┌───────────┐ │            │
                    │   │ structured │◄│    LLM    │◄┼──── context│
                    │   │ diagnosis  │ │ (env-only)│ │            │
                    │   └────────────┘ └───────────┘ │            │
                    │                         ▲       │            │
                    │                   ┌─────┴────┐  │            │
                    │                   │ CONTEXT  │◄┼────────────┘
                    │                   │ BUILDER  │  │
                    │                   └──────────┘  │
                    │  backend/data/errors/*.md ──────┘ (ingested via /api/index)
                    └──────────────────────────────────────────────┘
```

## RAG Pipeline

```
USER INPUT → ERROR ANALYZER → QUERY BUILDER → EMBEDDING MODEL → CHROMADB
     → RELEVANT DOCUMENTS → CONTEXT BUILDER → LLM → STRUCTURED DIAGNOSIS → FRONTEND
```

*Analyzer:* regex engine → language, error, category, keywords, stack frames ·
*Query:* "Java NullPointerException User getName null object causes fixes" ·
*Embeddings:* sentence-transformers / all-MiniLM-L6-v2 · *Search:* ChromaDB
cosine over section chunks (top 4–6, deduped) · *Context:* ERROR INFORMATION +
RETRIEVED KNOWLEDGE grants · *LLM:* OpenAI-compatible chat completions with a
strict grounding prompt → diagnosis with required headings + confidence + sources.

## Technology Stack

| Layer     | Technology                                                    |
|-----------|---------------------------------------------------------------|
| Frontend  | React 18, Vite 5, Tailwind CSS 3, react-markdown              |
| Backend   | Python 3.12+, FastAPI, Pydantic v2, uvicorn                   |
| RAG       | sentence-transformers, ChromaDB (persistent)                  |
| LLM       | Any OpenAI-compatible API (`openai` client, env-driven)       |
---

## Installation

Prerequisites: **Python 3.11+** and **Node.js 18+**.

### 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Frontend

```bash
cd ../frontend   # or open a second terminal
npm install
```

### 3. Environment configuration

Copy the example config and fill in your LLM credentials:

```bash
cp .env.example .env
```

Fill in at least:

```dotenv
LLM_API_KEY=sk-...          # your OpenAI-compatible API key
LLM_BASE_URL=               # blank for OpenAI; or http://localhost:11434/v1 (Ollama)
LLM_MODEL=gpt-4o-mini       # or e.g. llama3.2
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

The `.env` file is loaded automatically from the project root (or `backend/.env`).
**Never commit `.env`.** Without an LLM key the app still fully works for
*retrieval* (`/api/search`, `/api/health`), and `/api/analyze` returns a clear,
friendly message until the key is added.

---

## Running Backend

```bash
cd backend
python run.py
```

or explicitly:

```bash
cd backend
.venv\Scripts\activate
uvicorn app.main:app --reload --port 8000
```

On first startup the backend **ingests the knowledge base** (downloads the
embedding model once, ~90 MB) and writes the persistent ChromaDB store to
`backend/chroma_db`. Later startups reuse the store without re-embedding.

<details>
<summary>Manual re-indexing</summary>

```bash
cd backend
.venv\Scripts\activate
python ingest.py --force
# or via API
# curl -X POST "http://localhost:8000/api/index?force=true"
```

</details>

Interactive API docs: <http://localhost:8000/docs>.

## Running Frontend

```bash
cd frontend
npm run dev
```

Open <http://localhost:5173> — the Vite dev server proxies `/api` to
`http://localhost:8000`. Production build: `npm run build && npm run preview`.

---

## Example Usage

1. Open the UI → paste an error or click **Try Example**.
2. Optionally force a **Language** instead of Auto Detect.
3. Click **Analyze Error**.

Output includes:

- **Error Detected** — e.g. `NullPointerException` (+ language, category, type)
- **Confidence** — High / Medium / Low with a plain-language reason
- **Diagnosis** — Markdown with the exact required sections
- **Retrieved Knowledge** — the sources used, with relevance; click one to read it

Try these inputs:

```text
Exception in thread "main" java.lang.NullPointerException:
  Cannot invoke "User.getName()" because "user" is null
    at UserService.java:42
```

```text
Traceback (most recent call last):
  File "app/users.py", line 12, in <module>
    profile = user_profile['settings']
KeyError: 'settings'
```

```text
TypeError: Cannot read properties of undefined (reading 'toUpperCase')
    at normalizeName (utils.js:15)
```

```text
SELECT * FROM users WHERE id = NULL;
```
---

## API

| Method | Endpoint                  | Description                                   |
|--------|---------------------------|-----------------------------------------------|
| GET    | `/api/health`             | Status, LLM config, indexed chunk count       |
| POST   | `/api/analyze`            | Full pipeline → structured diagnosis + sources|
| POST   | `/api/search`             | Retrieval only (no LLM)                       |
| POST   | `/api/index`              | (Re)ingest the knowledge base (`?force=true`) |
| GET    | `/api/examples`           | Built-in example errors                       |
| GET    | `/api/documents`          | List knowledge documents                      |
| GET    | `/api/documents/{name}`   | Full Markdown source document                 |

### `POST /api/analyze`

Request:

```json
{ "input": "java.lang.NullPointerException at UserService.java:42", "language": "auto" }
```

Response (abridged):

```json
{
  "detected_error": "NullPointerException",
  "language": "Java",
  "language_confidence": "High",
  "category": "Runtime Error",
  "error_type": "NullPointerException",
  "confidence": "High",
  "confidence_reason": "error type detected; language detected (Java); strongly relevant knowledge found; keywords match retrieved material",
  "diagnosis": "## Diagnosis\n\n...",
  "sources": [
    {
      "source_file": "java_null_pointer_exception.md",
      "error_name": "NullPointerException",
      "language": "Java",
      "section": "Common Causes",
      "similarity": 0.71,
      "relevance": "High",
      "content": "### Common Causes ..."
    }
  ],
  "keywords": ["null", "user", "getname"],
  "rag_query": "Java NullPointerException user null object causes fixes",
  "warnings": []
}
```

---

## Project Structure

```
errorlens/
│
├── .env.example  .gitignore  README.md
│
├── frontend/
│   ├── index.html  package.json  vite.config.js  tailwind.config.js  postcss.config.js
│   └── src/
│       ├── main.jsx  App.jsx  index.css
│       ├── pages/        Workspace.jsx
│       ├── components/   Header, InputPanel, ResultPanel, SourcesPanel,
│       │                 ConfidenceBadge, DocumentModal, ErrorBanner, MarkdownView
│       └── services/     api.js
│
├── backend/
│   ├── requirements.txt  pytest.ini  run.py  ingest.py
│   ├── app/
│   │   ├── config.py  models.py  main.py
│   │   ├── api/          routes.py
│   │   ├── rag/          document_loader.py  chunker.py  embeddings.py
│   │   │                 vector_store.py  ingestion.py  retriever.py  prompts.py
│   │   └── services/     error_analyzer.py  query_builder.py  context_builder.py
│   │                     confidence.py  examples.py  llm.py
│   ├── data/errors/      36 knowledge documents (*.md)
│   ├── chroma_db/        persistent vector store (generated)
│   └── tests/            conftest + analyzer/loader/chunker/retrieval/api/e2e
└── ...
```

---

## Testing

```bash
cd backend
.venv\Scripts\activate
python -m pytest
```

Covered:

- Error detection (NPE, KeyError, JS TypeError, SQL NULL, custom exceptions)
- Language detection (auto, forced, unknown — never invented)
- Document loading (≥25 docs, frontmatter, required sections, path-traversal guard)
- Section-based chunking (metadata correctness, unique ids, long-section splitting)
- ChromaDB retrieval (relevance, dedup across sections, language filter)
- API endpoints (health, analyze, search, examples, documents, validation errors,
  friendly 503 when the LLM is missing)
- **End-to-end test**: real user error → analyzer → query builder → ChromaDB
  retrieval over real documents → context builder → (mocked) LLM → final
  diagnosis with cited sources.

The test suite uses a deterministic fake embedding model, so **no model download
is needed to run tests**.

---

## Future Improvements

- Additional language knowledge packs (Go, Rust, C#) — just add more `.md`
  documents and re-index.
- Retrieval reranking (cross-encoders) for tighter top-k precision.
- Optional hybrid search (BM25 lexical + vector) for stack-trace-heavy queries.
- Source statistics in the UI (most-retrieved errors).
- Streaming LLM responses for long diagnostics.
- Docker Compose setup for one-command local startup.

---

## License

MIT — use it, learn from it, improve it.