"""LLM service: calls any OpenAI-compatible chat completions API.

Configuration comes exclusively from environment variables:

    LLM_API_KEY    OpenAI-compatible API key
    LLM_BASE_URL   Base URL (e.g. https://api.openai.com/v1 or an Ollama/LM
                   Studio local endpoint). If empty, the OpenAI default is used.
    LLM_MODEL      Model name (e.g. gpt-4o-mini, llama3.2, qwen2.5)

The module is intentionally modular: swap chat_completions() for something
else and the rest of the pipeline is unaffected.
"""
from typing import Optional

from app.config import get_settings
from app.rag.prompts import SYSTEM_PROMPT, build_user_prompt


class LLMError(Exception):
    """Raised when the LLM call itself fails."""


class LLMNotConfiguredError(Exception):
    """Raised when no API key is available and no base URL is set."""


def _build_client():
    settings = get_settings()
    from openai import OpenAI

    kwargs = {"api_key": settings.llm_api_key or "sk-local-placeholder", "timeout": settings.llm_timeout}
    if settings.llm_base_url:
        kwargs["base_url"] = settings.llm_base_url
    return OpenAI(**kwargs)


def chat_completions(
    user_input: str,
    error_info: dict,
    retrieved_context: str,
    model: Optional[str] = None,
) -> str:
    """Call the LLM with the ErrorLens system prompt + assembled context.

    Returns the raw markdown diagnosis text.
    """
    settings = get_settings()
    if not settings.llm_configured:
        raise LLMNotConfiguredError(
            "LLM is not configured. Set LLM_API_KEY (and optionally LLM_BASE_URL "
            "and LLM_MODEL) in the .env file."
        )

    client = _build_client()
    try:
        response = client.chat.completions.create(
            model=model or settings.llm_model,
            temperature=settings.llm_temperature,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        error_info=error_info,
                        retrieved_context=retrieved_context,
                        user_input=user_input,
                    ),
                },
            ],
        )
    except Exception as exc:  # network / auth / rate-limit
        raise LLMError(f"LLM request failed: {type(exc).__name__}: {exc}") from exc

    content = (response.choices[0].message.content or "").strip()
    if not content:
        raise LLMError("LLM returned an empty response.")

    return content


def is_configured() -> bool:
    return get_settings().llm_configured