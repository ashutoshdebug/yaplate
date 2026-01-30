import asyncio
from typing import Optional

from google import genai

from app.logger import get_logger
from app.settings import GEMINI_API_KEY


logger = get_logger("yaplate.nlp.gemini")

_MODEL = "gemini-3-flash-preview"
_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client

    if _client is not None:
        return _client

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not set")

    _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def _generate_sync(prompt: str) -> str:
    client = _get_client()

    response = client.models.generate_content(
        model=_MODEL,
        contents=prompt,
    )

    if hasattr(response, "text") and response.text:
        return response.text.strip()

    try:
        parts = response.candidates[0].content.parts
        if parts and parts[0].text:
            return parts[0].text.strip()
    except Exception:
        pass

    retry_prompt = "Summarize this clearly:\n\n" + prompt[:12000]
    retry = client.models.generate_content(
        model=_MODEL,
        contents=retry_prompt,
    )

    if hasattr(retry, "text") and retry.text:
        return retry.text.strip()

    return "Unable to generate response (empty model output)."


async def gemini_generate(prompt: str) -> str:
    """
    Async-safe Gemini text generation.
    """
    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, _generate_sync, prompt)
    except Exception:
        # Preserve original behavior: bubble up
        logger.exception("Gemini generation failed")
        raise


async def detect_language_with_gemini(text: str) -> str:
    prompt = f"""
Detect the primary human language of the following text.
Return ONLY the ISO 639-1 two-letter code (like en, hi, ja, zh, fr, de).
No explanation.

Text:
{text}
"""
    result = await gemini_generate(prompt)
    return result.strip().lower()
