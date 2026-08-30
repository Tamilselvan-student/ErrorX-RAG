"""Minimal OpenAI-compatible mock server for local testing.

This lets you exercise the full ErrorLens pipeline (retrieval → context → LLM
diagnosis) without an API key. It inspects the user message that the ErrorLens
backend sends: if retrieved knowledge chunks are present, the diagnosis echoes
the source filenames (proving the RAG context reached the LLM).

Usage:
    python scripts/mock_llm.py            # serves on http://127.0.0.1:9001/v1

Then in your .env:
    LLM_BASE_URL=http://127.0.0.1:9001/v1
    LLM_API_KEY=mock-key
"""
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title="ErrorLens Mock LLM")


def _read_knowledge_sources(user_message: str):
    """Return the source files mentioned in the user message (if any)."""
    sources = []
    for line in user_message.splitlines():
        if line.startswith("Source: "):
            name = line[len("Source: "):].strip()
            if name and name not in sources:
                sources.append(name)
    return sources


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()
    messages = body.get("messages", [])
    model = body.get("model", "mock-llm")

    user_message = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
    sources = _read_knowledge_sources(user_message)

    if sources:
        source_list = "\n".join(f"- {s}" for s in sources)
        grounded = "The diagnosis is grounded in the following retrieved knowledge:"
    else:
        source_list = "*(no knowledge sources were present in the context)*"
        grounded = "No retrieved knowledge reached the LLM."

    content = (
        "## Diagnosis\n\n"
        f"{grounded}\n\n{source_list}\n\n"
        "## What This Error Means\n\n"
        "The input describes a programming error. This diagnosis was generated "
        "from knowledge retrieved via the ErrorLens RAG pipeline.\n\n"
        "## Likely Root Cause\n\n"
        "- The package/type or value described in the input is not in the state the code expects.\n\n"
        "## How To Fix It\n\n"
        "1. Inspect the line identified by the stack trace.\n"
        "2. Add a guard for the unexpected value.\n\n"
        "## Example\n\n```python\nresult = maybe() or fallback\n```\n\n"
        "## How To Prevent It\n\n"
        "- Validate input at the boundary.\n\n"
        "## Related Errors\n\n"
        "- See the knowledge documents above for related errors."
    )

    return {
        "id": "chatcmpl-mock-1",
        "object": "chat.completion",
        "created": 0,
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 100, "completion_tokens": 80, "total_tokens": 180},
    }


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=9001, log_level="warning")