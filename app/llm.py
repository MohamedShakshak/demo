import cohere
from cohere.core.api_error import ApiError
from fastapi import HTTPException

from .config import settings
from .schemas import ChatMessage

# One client for the whole app (reuses HTTP connections).
_client: cohere.AsyncClientV2 | None = None


def get_client() -> cohere.AsyncClientV2:
    global _client
    if not settings.cohere_api_key:
        raise HTTPException(status_code=503, detail="COHERE_API_KEY is not configured")
    if _client is None:
        _client = cohere.AsyncClientV2(api_key=settings.cohere_api_key, timeout=60)
    return _client


async def chat(messages: list[ChatMessage]) -> str:
    client = get_client()
    try:
        response = await client.chat(
            model=settings.cohere_model,
            messages=[m.model_dump() for m in messages],
        )
    except ApiError as e:
        raise HTTPException(status_code=502, detail=f"Cohere error: {e.body}") from e
    except Exception as e:  # network errors, timeouts
        raise HTTPException(status_code=504, detail=f"Cohere unreachable: {e}") from e

    # Content is a list of parts; keep only text (skip e.g. "thinking" parts).
    parts = response.message.content or []
    return "".join(p.text for p in parts if getattr(p, "type", None) == "text")
