from langdetect import detect, DetectorFactory
from collections import Counter
import re
from app.nlp.gemini_client import detect_language_with_gemini

DetectorFactory.seed = 0  # deterministic results


def safe_detect(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


async def detect_with_fallback(title: str, body: str) -> str:
    title = (title or "").strip()
    body = (body or "").strip()

    # 🔒 HARD RULE: If body is empty, force English
    if not body:
        return "en"

    texts = []

    # Split body into meaningful chunks
    parts = re.split(r"[。\n.!?]", body)
    texts.extend([p.strip() for p in parts if len(p.strip()) > 10])

    # Fallback: if body chunks are too small, still force English
    if not texts:
        return "en"

    langs = [safe_detect(t) for t in texts if t.strip()]

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
        pass

    return dominant
