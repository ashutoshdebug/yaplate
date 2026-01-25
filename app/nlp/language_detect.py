from langdetect import detect, DetectorFactory
from collections import Counter
import re
from app.nlp.gemini_client import detect_language_with_gemini  # you'll add this

DetectorFactory.seed = 0  # deterministic results


def safe_detect(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"


async def detect_with_fallback(title: str, body: str) -> str:
    texts = []

    if body and body.strip():
        parts = re.split(r"[。\n.!?]", body)
        texts.extend([p.strip() for p in parts if len(p.strip()) > 10])
    else:
        texts.append(title)

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
