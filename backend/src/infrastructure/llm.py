from functools import lru_cache

from langchain_groq import ChatGroq

from src.infrastructure.config import settings


@lru_cache(maxsize=1)
def get_llm() -> ChatGroq:

    if (
        settings.groq_api_key is None
        or not settings.groq_api_key.get_secret_value()
    ):
        raise RuntimeError(
            "GROQ_API_KEY is not configured."
        )

    return ChatGroq(
        api_key=settings.groq_api_key.get_secret_value(),
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        timeout=settings.llm_timeout,
        max_retries=settings.llm_max_retries,
        reasoning_effort=settings.llm_reasoning_effort
    )