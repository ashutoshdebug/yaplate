from app.nlp.gemini_client import gemini_generate

KEYWORDS = [
    "maintainer", "approval", "approve", "review", "reviewer",
    "merge", "merging", "owner", "decision", "waiting for"
]

async def wants_maintainer_attention(text: str) -> bool:
    text_l = text.lower()

    # 1. Deterministic keyword gate (fast + safe)
    if any(k in text_l for k in KEYWORDS):
        return True

    # 2. Gemini semantic fallback
    prompt = f"""
Decide if this message means the author is waiting for maintainer or reviewer action.
Reply only YES or NO.

Message:
{text}
"""
    try:
        resp = await gemini_generate(prompt)
        return resp.strip().lower().startswith("yes")
    except Exception:
        return False
