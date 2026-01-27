from app.settings import LINGO_API_KEY
from lingodotdev import LingoDotDevEngine
# import os
from app.nlp.glossary import build_reference
from app.nlp.llm_guard import safe_llm_call

API_KEY = LINGO_API_KEY

async def translate(text: str, target: str) -> str:
    reference = build_reference(target)

    async with LingoDotDevEngine({"api_key": API_KEY}) as engine:
        return await safe_llm_call(
            engine.localize_text,
            text,
            {
                "target_locale": target,
                "reference": reference,
                "fast": True
            }
        )
