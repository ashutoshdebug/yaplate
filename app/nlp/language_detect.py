import re
import asyncio
from collections import Counter
from typing import List

from langdetect import detect, DetectorFactory

from app.logger import get_logger
from app.nlp.gemini_client import detect_language_with_gemini


DetectorFactory.seed = 0  # deterministic results

logger = get_logger("yaplate.nlp.language_detect")


def _safe_detect_sync(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


async def _safe_detect(text: str) -> str:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _safe_detect_sync, text)


async def detect_with_fallback(title: str, body: str) -> str:
    title = (title or "").strip()
    body = (body or "").strip()

    # 🔒 HARD RULE: If body is empty, force English
    if not body:
        return "en"

    # Split body into meaningful chunks
    parts = re.split(r"[。\n.!?]", body)
    texts: List[str] = [p.strip() for p in parts if len(p.strip()) > 10]

    # Fallback: if body chunks are too small, still force English
    if not texts:
        return "en"

    # Run language detection concurrently (non-blocking)
    tasks = [_safe_detect(t) for t in texts if t.strip()]
    langs = await asyncio.gather(*tasks, return_exceptions=False)

    if not langs:
        return "en"

    freq = Counter(langs)
    dominant, count = freq.most_common(1)[0]

    # High confidence
    if count > 1:
        return dominant

    # Low confidence → ask Gemini
    combined = f"Title: {title}\n\nBody: {body}"
    try:
        gemini_lang = await detect_language_with_gemini(combined)
        if gemini_lang:
            gemini_lang = gemini_lang.strip().lower()
            if len(gemini_lang) == 2:
                return gemini_lang
    except Exception:
        logger.exception("Gemini language detection failed")

    return dominant
