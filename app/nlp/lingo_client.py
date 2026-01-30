from app.settings import LINGO_API_KEY
from lingodotdev import LingoDotDevEngine

from app.logger import get_logger
from app.nlp.glossary import build_reference
from app.nlp.llm_guard import safe_llm_call


logger = get_logger("yaplate.nlp.lingo")

API_KEY = LINGO_API_KEY


async def translate(text: str, target: str) -> str:
    """
    Translate text to target language using LingoDotDev.
    Behavior and fallback semantics are intentionally stable.
    """
    # Defensive normalization (no behavior change)
    text = text or ""
    target = target or ""

    reference = build_reference(target)

    try:
        async with LingoDotDevEngine({"api_key": API_KEY}) as engine:
            return await safe_llm_call(
                engine.localize_text,
                text,
                {
                    "target_locale": target,
                    "reference": reference,
                    "fast": True,
                },
            )
    except Exception:
        # Preserve behavior: safe_llm_call decides fallback,
        # but engine setup errors must still be visible
        logger.exception("Lingo translation failed")
        raise
