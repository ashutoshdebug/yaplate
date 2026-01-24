from langdetect import detect, DetectorFactory
from collections import Counter
import re

DetectorFactory.seed = 0  # deterministic results

def safe_detect(text: str) -> str:
    try:
        return detect(text)
    except Exception:
        return "en"

def detect_dominant_language(title: str, body: str) -> str:
    texts = []

    if body and body.strip():
        # Split by sentences / newlines
        parts = re.split(r"[。\n.!?]", body)
        texts.extend([p.strip() for p in parts if len(p.strip()) > 10])
    else:
        texts.append(title)

    langs = [safe_detect(t) for t in texts]

    if not langs:
        return "en"

    freq = Counter(langs)
    dominant, count = freq.most_common(1)[0]

    # If weak confidence (tie or all single), fallback to title
    if count == 1 and title:
        return safe_detect(title)

    return dominant
